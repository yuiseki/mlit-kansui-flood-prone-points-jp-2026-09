import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))
import kansui

sys.path.insert(0, str(Path(__file__).parents[1] / "scripts"))


def test_kml_url_uses_https_and_kml_dir():
    base = "http://www.thr.mlit.go.jp/road/doro_bosaijoho_webmap"
    assert kansui.kml_url(base, "02_aomori_kansui_point") == (
        "https://www.thr.mlit.go.jp/road/doro_bosaijoho_webmap/kml/02_aomori_kansui_point.kml"
    )


def test_parse_bases():
    assert kansui.parse_bases("a b\nc d\n") == {"a": "b", "c": "d"}


@pytest.mark.parametrize(
    "base,bureau",
    [
        ("https://www.ktr.mlit.go.jp/honkyoku/road/x", "ktr"),
        ("https://www.qsr.mlit.go.jp/n-michi/x", "qsr"),
    ],
)
def test_bureau_of(base, bureau):
    assert kansui.bureau_of(base) == bureau


def test_layer_parts():
    assert kansui.layer_parts("12_chiba_kansui_point") == ("12", "chiba")
    with pytest.raises(ValueError):
        kansui.layer_parts("chiba")


KML = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2"><Document>
<!-- A-02-001 -->
<Placemark><name> 青森市 </name><description><![CDATA[<table><tr><td>箇所表</td><td><a href="../attachment/aomoriken-02-201.pdf" target="_blank">x</a></td></tr></table>]]></description>
<styleUrl>#S</styleUrl><Point><coordinates>140.81735,40.846249</coordinates></Point></Placemark>
<!-- A-02-002 2019/05/29 deleted
<Placemark><name>gone</name><Point><coordinates>1,2</coordinates></Point></Placemark> -->
<Placemark><name>b</name><description><![CDATA[<a href="https://x.example/attachment/b-02-1.pdf">p</a>]]></description>
<styleUrl>#S</styleUrl><Point><coordinates>141.0,41.0,0</coordinates></Point></Placemark>
</Document></kml>"""


def test_parse_kml_reads_only_live_placemarks():
    import export

    rows, withdrawn = export.parse_kml(
        KML, "https://www.thr.mlit.go.jp/road/doro_bosaijoho_webmap"
    )
    assert [r["name"] for r in rows] == ["青森市", "b"]
    assert withdrawn == 1
    assert rows[0]["lon"] == 140.81735 and rows[0]["lat"] == 40.846249
    assert rows[0]["pdf_href"] == "../attachment/aomoriken-02-201.pdf"
    assert (
        rows[0]["pdf_url"]
        == "https://www.thr.mlit.go.jp/road/doro_bosaijoho_webmap/attachment/aomoriken-02-201.pdf"
    )
    assert rows[0]["pdf_key"] == "aomoriken-02-201"
    assert rows[1]["pdf_url"] == "https://x.example/attachment/b-02-1.pdf"
    assert rows[1]["lon"] == 141.0 and rows[1]["lat"] == 41.0


def test_publish_refuses_while_the_licence_is_unconfirmed():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "publish", Path(__file__).parents[1] / "src" / "publish.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    with pytest.raises(SystemExit, match="licence is not confirmed"):
        mod.collect()
