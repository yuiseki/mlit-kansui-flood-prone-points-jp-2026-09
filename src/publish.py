#!/usr/bin/env python3
"""Push the card, licence, provenance, the KML files as fetched, the Parquet, the evidence and the docs to the Hub in one commit.

uv run python src/publish.py             # dry run: list the files and their sizes
uv run python src/publish.py --push      # prints the commit sha and writes docs/revision.json

Refuses to run unless docs/licence_status.json says that PDL1.0 was confirmed from a saved source.
"""

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPO = "yuiseki/kansui-flood-prone-points-jp-2026-09"
DOCS = [
    "export_log.json",
    "verify_local.json",
    "prefecture_check.json",
    "prefecture_outliers.tsv",
    "licence_status.json",
]


def collect() -> dict[str, Path]:
    st = json.loads((ROOT / "docs" / "licence_status.json").read_text())
    card = (DATA / "README.md").read_text(encoding="utf-8")
    if not st["pdl1.0_confirmed"] or "license_name: pdl-1.0" not in card:
        raise SystemExit("the licence is not confirmed: do not publish")
    run = max((DATA / "raw").glob("*/MANIFEST.json")).parent
    man = json.loads((run / "MANIFEST.json").read_text())
    ver = json.loads((ROOT / "docs" / "verify_local.json").read_text())
    if ver["problems"] or f"{ver['rows']:,}" not in card:
        raise SystemExit("the local verification or the card does not match the table")
    files = {"README.md": DATA / "README.md", "LICENSE": DATA / "LICENSE", "provenance.yaml": DATA / "provenance.yaml",
             f"raw/{run.name}/MANIFEST.json": run / "MANIFEST.json",
             "parquet/kansui_points.parquet": DATA / "parquet" / "kansui_points.parquet"}  # fmt: skip
    for layer, m in man["files"].items():
        p = run / "kml" / f"{layer}.kml"
        if hashlib.sha256(p.read_bytes()).hexdigest() != m["sha256"]:
            raise SystemExit(f"{layer} is not the file in its manifest")
        files[f"raw/{run.name}/kml/{layer}.kml"] = p
    for p in sorted((ROOT / "evidence" / "pages").glob("*")):
        files[f"evidence/pages/{p.name}"] = p
    for d in DOCS:
        files[f"docs/{d}"] = ROOT / "docs" / d
    for s in sorted((ROOT / "scripts").glob("*.py")):
        files[f"scripts/{s.name}"] = s
    missing = [k for k, v in files.items() if not v.is_file()]
    if missing:
        raise SystemExit(f"missing: {missing}")
    return files


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=REPO)
    ap.add_argument("--push", action="store_true")
    a = ap.parse_args()
    files = collect()
    total = sum(p.stat().st_size for p in files.values())
    print(f"{a.repo}\n  {len(files)} files, {total:,} bytes")
    if not a.push:
        print("\ndry run. pass --push to upload")
        return 0
    from huggingface_hub import CommitOperationAdd, HfApi

    api = HfApi()
    api.create_repo(a.repo, repo_type="dataset", exist_ok=True, private=False)
    ops = [
        CommitOperationAdd(path_in_repo=k, path_or_fileobj=str(p))
        for k, p in files.items()
    ]
    info = api.create_commit(a.repo, ops, repo_type="dataset", commit_message="Flood-prone road points (冠水想定箇所) of the MLIT bureaus")  # fmt: skip
    sums = {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in files.items()}
    (ROOT / "docs" / "revision.json").write_text(
        json.dumps({"repo": a.repo, "revision": info.oid, "sha256": sums}, indent=1)
        + "\n"
    )
    print("pushed", a.repo, "revision", info.oid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
