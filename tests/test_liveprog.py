from pathlib import Path

from eelwizard.corpus.liveprog import normalize_liveprog, parse_liveprog
from eelwizard.models import HostProfile, SourceClass

FIXTURE = Path("tests/fixtures/upstream_gainControl.eel")


def test_parse_gain_control() -> None:
    doc = parse_liveprog(FIXTURE.read_text(encoding="utf-8"))
    assert doc.description == "Gain control"
    assert doc.tags == ["gain"]
    assert list(doc.sections) == ["init", "sample"]
    assert [c.name for c in doc.controls] == ["dB"]
    assert "gainLin = exp" in doc.sections["init"]


def test_normalize_gain_control() -> None:
    text = FIXTURE.read_text(encoding="utf-8")
    record = normalize_liveprog(
        name="gainControl",
        text=text,
        source_path="app/src/main/assets/Liveprog/gainControl.eel",
        source_class=SourceClass.SHIPPED,
        host_profile=HostProfile.ROOTLESS_UPSTREAM,
    )
    assert record.sections == ["init", "sample"]
    assert record.controls == ["dB"]
    assert record.host_variables == ["spl0", "spl1"]
    assert len(record.content_hash) == 64
