# Licence findings (2026-10-30)

Question: is the KML of 冠水想定箇所 under the Public Data License 1.0 (PDL1.0), as reported to us?

Read, for each of the seven bureaus (thr, ktr, hrr, cbr, kkr, skr, qsr) and for the Chugoku bureau (cgr): the top page
of the 道路防災情報Webマップ (`main/index.html`), the map page (`main/map.html`, for ktr), one list page (ktr Chiba), the
map script (`js/doro_bousai.js`, `js/config.js`, for ktr). Saved under `evidence/pages/`.

Result: none of these pages contains a licence or terms statement (searched for 利用規約, 公共データ, ライセンス, 二次利用,
著作権, オープンデータ). The pages say only that the background map is the GSI's 地理院地図 and give the update dates
(冠水想定箇所: 平成25年9月 for ktr; 令和8年3月 for cgr), and a contact. The directory URLs of the web maps answer 403 (no
index); the KML files themselves answer 200 with `application/vnd.google-earth.kml+xml` at
`<base>/kml/<NN>_<pref>_kansui_point.kml` (the path is in the map script: `'../kml/' + pref + '.kml'`).

Web searches (two, standard and extended) did not find a PDL1.0 statement for these KML either. A bureau-wide or
MLIT-wide site policy was not used as evidence (not the data's own statement).

Open: where did the PDL1.0 statement come from (a page of the bureaus, MLIT, or the data portal)? Save it under
`evidence/` and set `pdl1.0_confirmed` to true in `docs/licence_status.json`; `src/publish.py` refuses until then.

Other regions: 北海道 and 沖縄県: no KML of the same kind found (the search result for 沖縄 led to a page that redirects to the
Okinawa General Bureau's top page; a Hokkaido web map was not located). 中国地方整備局: found, 5 KML (31 to 35), added.
