"""Constants and helpers shared by the scripts of kansui-flood-prone-points-jp."""

import re
from pathlib import Path

UA = "Mozilla/5.0 (research; yuiseki)"
PAUSE_S = 2.0
# the map's script (js/doro_bousai.js) loads '../kml/' + layer + '.kml' relative to <base>/main/
BASES_FILE = "bases.txt"


def kml_url(base: str, layer: str) -> str:
    return f"{base.replace('http://', 'https://')}/kml/{layer}.kml"


def parse_bases(text: str) -> dict[str, str]:
    return dict(line.split() for line in text.splitlines() if line.strip())


def bureau_of(base: str) -> str:
    m = re.match(r"https?://www\.([a-z]+)\.mlit\.go\.jp/", base)
    if not m:
        raise ValueError(base)
    return m.group(1)


def layer_parts(layer: str) -> tuple[str, str]:
    m = re.match(r"^(\d{2})_([a-z]+)_kansui_point$", layer)
    if not m:
        raise ValueError(layer)
    return m.group(1), m.group(2)


def root() -> Path:
    return Path(__file__).resolve().parents[1]
