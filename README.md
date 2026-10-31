# mlit-kansui-flood-prone-points-jp-2026-09

Scripts that collect the 冠水想定箇所 KML files of the eight regional bureaus of the MLIT (道路防災情報Webマップ), write them
as GeoParquet, verify them, and publish them.

The data and its card are on Hugging Face: <https://huggingface.co/datasets/yuiseki/mlit-kansui-flood-prone-points-jp-2026-09>
(published at revision `d4e2e1f6a3278a9956044094acd852a73c5283f2`; `docs/revision.json`).

- `scripts/00_terms.py`: read and save the terms pages of each bureau (the publication gate reads its result).
- `scripts/01_collect.py`, `02_export_parquet.py`, `03_verify.py`, `05_check_prefecture.py`: collect, export, verify.
- `scripts/04_card.py`: write the card, `src/publish.py`: publish, `scripts/06_verify_hub.py`: read the Hub copy back.
- `scripts/07`-`10`: the reading of the 箇所表 PDFs, which belongs to the companion dataset
  `mlit-kansui-flood-prone-points-pdf-jp-2026-09`.

The code is offered as is; the data is under the terms of the bureaus (PDL1.0), see the card.
