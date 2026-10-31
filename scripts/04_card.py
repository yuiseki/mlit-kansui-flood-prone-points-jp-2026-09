#!/usr/bin/env python3
"""Write data/README.md (the Hub card), data/LICENSE and data/provenance.yaml from the generated docs.

    uv run python scripts/04_card.py

The licence block is PDL1.0 only for bureaus that docs/licence_status.json (written by 00_terms.py) confirms.
"""

import json

import geopandas as gpd
import pandas as pd
import kansui

ROOT = kansui.root()
REPO = "kansui-flood-prone-points-jp-2026-09"


BUREAU_NAMES = [
    "東北地方整備局",
    "関東地方整備局",
    "北陸地方整備局",
    "中部地方整備局",
    "近畿地方整備局",
    "四国地方整備局",
    "九州地方整備局",
    "中国地方整備局",
]


def bureau_ids() -> list[str]:
    return ["thr", "ktr", "hrr", "cbr", "kkr", "skr", "qsr", "cgr"]


def main() -> int:
    st = json.loads((ROOT / "docs" / "licence_status.json").read_text())
    bt = json.loads((ROOT / "docs" / "bureau_terms.json").read_text())
    run = max((ROOT / "data" / "raw").glob("*/MANIFEST.json")).parent
    man = json.loads((run / "MANIFEST.json").read_text())
    g = gpd.read_parquet(ROOT / "data" / "parquet" / "kansui_points.parquet")
    ex = json.loads((ROOT / "docs" / "export_log.json").read_text())
    chk = json.loads((ROOT / "docs" / "prefecture_check.json").read_text())
    al = json.loads((ROOT / "docs" / "attach_log.json").read_text())
    pl = json.loads((ROOT / "docs" / "pdf_parse_log.json").read_text())
    pv = json.loads((ROOT / "docs" / "pdf_verify.json").read_text())
    mc = json.loads((ROOT / "docs" / "manual_check.json").read_text())
    jj = pd.read_parquet(ROOT / "data" / "parquet" / "kansui_points_joined.parquet")
    jok = jj[jj["pdf_parse_status"] == "ok"]
    fur = int((jj["pdf_name_cells"] == "furigana_in_source_not_published").sum())
    nok = len(jok)
    mg = int((~jok["pdf_mgmt_no"].astype(str).str.match(r"^.{2,4}[都道府県]-\d\d-\d{1,3}(-\d)?$")).sum())
    pman = json.loads((run / "PDF_MANIFEST.json").read_text())["files"]
    n404 = sum(1 for v in pman.values() if v["status"] == 404)
    layouts = "\n".join(f"| {k} | {v} |" for k, v in pl["by_layout_status"].items())
    matches = "\n".join(f"| {k} | {v} |" for k, v in al["match"].items())
    mods = sorted(m["last_modified"] for m in man["files"].values())
    ex0 = json.loads((ROOT / "docs" / "export_log.json").read_text())
    bureaus_in = sorted(
        {m["bureau"] for layer, m in man["files"].items() if layer in ex0["files"]}
    )
    all_ok = all(st["bureaus"][b]["confirmed"] for b in bureaus_in)
    if all_ok:
        lic = "license: other\nlicense_name: pdl-1.0\nlicense_link: https://www.digital.go.jp/resources/open_data/public_data_license_v1.0"
    else:
        lic = "license: other\nlicense_name: unconfirmed"
    names = dict(zip(bureau_ids(), BUREAU_NAMES))
    bases = kansui.parse_bases(
        (ROOT / "data" / "bases_from_user.txt").read_text()
        + (ROOT / "data" / "bases_added.txt").read_text()
    )
    page = {}
    for base in bases.values():
        page.setdefault(
            kansui.bureau_of(base),
            base.replace("http://", "https://") + "/main/index.html",
        )
    quotes = "\n".join(
        f"- {names[b]} ({bt[b]['url']}):\n  > {bt[b]['use_sentence']}"
        for b in bureaus_in
    )
    attrib = "\n".join(
        f"- {names[b]}: 出典：{names[b]}ホームページ（{page[b]}）" for b in bureaus_in
    )
    proc = "\n".join(
        f"- {names[b]}: 「道路防災情報Webマップ 冠水想定箇所」（{names[b]}）（{page[b]}）を加工して作成"
        for b in bureaus_in
    )
    lic_text = f"""Each bureau's own site-wide terms say that its content is usable under the Public Data License 1.0
(公共データ利用規約 第1.0版, PDL1.0; compatible with CC BY 4.0), unless a right notice says otherwise. **The basis is the
bureaus' site-wide terms. No licence notice specific to the Webmap pages or the KML files exists** (the Webmap pages,
their scripts and the KML carry no rights notice: checked {man["fetched"]}). Judge for yourself whether the site-wide
terms reach these files. The pages were saved under `evidence/terms/`; the quotations are in `docs/bureau_terms.json`.

The Kinki (近畿) sentence, from <https://www.kkr.mlit.go.jp/link.html>:

> {bt["kkr"]["use_sentence"]}

The sentence of each bureau whose points are in this dataset:

{quotes}

The terms exclude symbol marks, logos and character designs, and content for which a separate rule is stated
(the Kyushu page adds that some content may be restricted by individual laws). The background map of the Webmaps is
the GSI's 地理院地図 and is not part of the data. The 箇所表 PDFs (not included here) hold GSI maps and photographs of
the sites; no rights mark other than the GSI map note was found on the 40 PDFs that were looked at.

Attribution, per bureau (出典：<局>ホームページ（URL）):

{attrib}

Processing notice (編集・加工等を行ったことの記載。国が作成したかのような態様で公表・利用してはいけません):

{proc}

This dataset is made by yuiseki from the KML files: the points were read and written as GeoParquet, with columns
added (see below); the original names and coordinates are kept. It was made by processing the bureaus' data and is
not made or endorsed by the State.
"""
    by_pref = g.groupby("pref").size()
    rows = "\n".join(f"| {p} | {n} |" for p, n in by_pref.items())
    bureaus = "\n".join(
        f"| {b} | {n} |" for b, n in g.groupby("bureau_ja").size().items()
    )
    card = f"""---
{lic}
language:
- ja
tags:
- japan
- flood
- road
- underpass
- point
size_categories:
- 1K<n<10K
pretty_name: Flood-prone road points (冠水想定箇所) of the MLIT regional bureaus, 45 prefectures
configs:
- config_name: joined
  data_files: parquet/kansui_points_joined.parquet
- config_name: points
  data_files: parquet/kansui_points.parquet
- config_name: pdf_records
  data_files: parquet/pdf_records.parquet
---

# {REPO}

{len(g):,} points of 冠水想定箇所 (road points where the road lies lower than the ground around it, for example
underpasses, which may flood in a local heavy rain) from the 道路防災情報Webマップ of eight regional bureaus of the
Ministry of Land, Infrastructure, Transport and Tourism (MLIT), 45 prefectures, as GeoParquet. Original names and
coordinates are kept.

## Source

KML files `<bureau site>/doro_bosaijoho_webmap/kml/<NN>_<prefecture>_kansui_point.kml` (the files the web maps load;
the URL of each is in `source_url` and in `raw/*/MANIFEST.json`), fetched {man["fetched"]}. Last-Modified of the
files ranges from {mods[0]} to {mods[-1]}; it differs per prefecture. The bureau pages state their update
dates for the 冠水想定箇所 as 平成25年9月 (2013) to 令和8年3月 (2026), per bureau. The 5 Chugoku prefectures were
added from the Chugoku bureau's map (not in the first list that was given).

## Licence

{lic_text}

## Rows

| Bureau | Points |
|---|---|
{bureaus}

| Prefecture | Points |
|---|---|
{rows}

## Columns

`fid`, `layer` (KML file name), `pref_code`, `pref_roma`, `pref`, `bureau`, `bureau_ja`, `name` (the Placemark
name), `lon`, `lat` (as in the KML, EPSG:4326), `pdf_href` (the link in the KML), `pdf_url` (resolved, https),
`pdf_key` (its file stem), `style_url`, `source_last_modified`, `source_url`, `geometry`.

## Attributes from the 箇所表 PDFs (config `joined`, table `pdf_records`)

Each KML point links to a 箇所表 PDF of the bureau ({al["points"] - al["match"].get("no_pdf", 0):,} points have a link; {len(pman)} unique PDFs,
fetched {man["fetched"]}, {n404} of them missing (HTTP 404)). The tables of the PDFs were read with pdfplumber, one row per
described point, **the text of every cell as published (only whitespace collapsed)**. **The PDFs themselves are not
redistributed**: they contain GSI maps and photographs of the sites. `raw/*/PDF_MANIFEST.json` and `pdf_sha256` give the
URL, size, Last-Modified and sha256 of each PDF. A cell that could not be read with certainty is null and the row
carries a `parse_status`; nothing was guessed.

| layout / parse_status | PDFs (records) |
|---|---|
{layouts}

`parse_status`: `ok` (all required cells read), `ambiguous` (a required cell is empty or unreadable; see `parse_note`),
`layout_unknown` (no known layout; all attributes null). Layout A: the 説明表 / 箇所表 / 様式 tables; layout B: the
道路冠水(危険)想定箇所 forms (石川, 富山, 新潟).

How the points are matched to the table (`pdf_match` in `joined`; the key is the PDF file linked in the KML):

| pdf_match | points |
|---|---|
{matches}

`pdf_unique`: the PDF is linked by this point only and holds one record; `pdf_shared`: the PDF is linked by several points or
holds several records, attributes are not attached (the records are in `pdf_records`); `no_pdf`; `pdf_missing`.
`pdf_key_consistent` compares the number in the file name with the number in the management number (a check only).

Checks: {pv["cells_checked"]:,} parsed cells of {pv["pdfs_checked"]} PDFs were looked up in `pdftotext -layout` of the same PDF
({pv["cells_not_in_pdftotext"]} not found; the count of 管理番号/整理番号 labels equals the record count except {pv["label_count_mismatch"]} PDFs).
Manual check: {mc["n"]} points drawn at random (seed {mc["seed"]}) were compared with the rendered text of their PDFs:
{mc["correct"]} of {mc["n"]} fully correct ({mc["note"]}).

Withheld cells: the 九州 bureau's PDFs (熊本県 150 points, 福岡県 138, 鹿児島県 50, 大分県 31, 宮崎県 20, 長崎県 16, 佐賀県 6) and 山形県 (48) print
the reading (furigana) of the names above the names (青森県, 宮城県, 千葉県 and 兵庫県 have one flagged point each, which may be a wrap
of a real name). The text of the PDF then runs the reading into the name cells, and the name cannot be told from the reading without
guessing. In `joined` the three cells `pdf_place_name`, `pdf_underpass_name` and `pdf_road_kind` of such a point are null and
`pdf_name_cells` says `furigana_in_source_not_published` (a point is flagged when a cell begins with a hiragana run and a space or
has a hiragana, a space and a hiragana: {fur:,} points);
`pdf_records` keeps the cells as read. The 管理番号 cell can carry a parse artefact (a lost hyphen as in 茨城県02-001 or 山形県02-204, or a
second line appended): {mg:,} of the {nok:,} points with attributes do not match the pattern 県名-02-nnn; the file stem `pdf_key` is the
reliable key.

Column mapping (published label in the PDF to column; the prefix `pdf_` is added in `joined`): 管理番号/整理番号 `mgmt_no`
(whitespace removed: a line break splits it), 箇所名称 `place_name`, 道路名 `road_name`, アンダーパス等名称/施設名
`underpass_name`, 種別 `road_kind`, 都道府県名/県名 `pref_name`, 市町村 `municipality`, 字丁目 `aza_chome`, 番地 `banchi`,
地先名 `sakimei`, 管理者 名称/TEL `manager_name`/`manager_tel`, 警察署 `police_name`/`police_tel`, 消防署 `fire_name`/`fire_tel`,
備考 `remarks`. In layout B the police and fire cells hold name and TEL together as published (`police_text`, `fire_text`),
and the manager's further cells are in `manager_tel_text`; the extra items of some forms (冠水範囲, 冠水原因, 排水ポンプの有無 ...)
are in `extra_cells` as JSON. `layout`, `record_no`, `parse_status`, `parse_note` describe the parse.

## What was changed

Only parsing: an XML parser reads each Placemark. Nothing was corrected. Two Placemarks that the publisher commented out
in the KML as withdrawn (京都府-02-020 and 大阪府-02-030, 2019/05/29) are not rows: {ex["withdrawn_total"]} withdrawn.

## Known issues (measured {man["fetched"]})

- {ex["rows_without_pdf"]} points have no link to a 箇所表 (all in 岩手県).
- The 箇所表 PDF is not unique per point: {ex["pdf_key_duplicates"]} rows repeat the `pdf_key` of another row
  (秋田県 uses one PDF for its points, 山形県 has shared ones). The PDFs hold the attributes of the points (the
  management number, the road, the underpass name, the address, the manager, the police and fire stations); see the
  section on the attributes.
- {chk["outside"]} of the {chk["points"]:,} points are outside the polygon of their stated prefecture
  (jp-admin-2026-09); {chk["outside_over_100m"]} of them by more than 100 m (3 in 宮城県 by about 35 km, 4 in 栃木県 by
  4 to 6 km). They are kept as published; the list is in `docs/prefecture_outliers.tsv`.
- {ex["name_duplicates_within_layer"]} rows repeat the name of another row of the same prefecture; {ex["coordinate_duplicates"]} repeat the coordinates.
- Not in the data: 北海道 and 沖縄県 (no KML of the same kind was found), and the web maps' other layers.
- The KML coordinates have 4 to 9 decimals; some are rounded to 4 decimals (about 10 m).

## Reproduce

`scripts/01_collect.py` (45 KMLs, a 2 s pause between requests), `02_export_parquet.py`, `03_verify.py` (GDAL's KML
reader as a second route), `05_check_prefecture.py`, `04_card.py`.
"""
    (ROOT / "data" / "README.md").write_text(card)
    (ROOT / "data" / "LICENSE").write_text(lic_text.replace("**", "") + "\n")
    (ROOT / "data" / "provenance.yaml").write_text(
        "source: MLIT regional bureaus, 道路防災情報Webマップ (kml)\n"
        f"fetched: {man['fetched']}\nfiles: {len(man['files'])}\nrows: {len(g)}\n"
        f"licence_confirmed_bureaus: {','.join(bureaus_in)}\nlicence_basis: site-wide terms of each bureau\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
