from pathlib import Path

from eelwizard.eel.lint import lint_liveprog
from eelwizard.eel.repair import apply_safe_repairs
from eelwizard.models import HostProfile

GOOD = Path("tests/fixtures/upstream_gainControl.eel").read_text(encoding="utf-8")
BROKEN = GOOD.replace("spl0 = spl0 * gainLin;", "spl0 = spl0 * gainLin", 1)


def test_missing_semicolon_is_line_12() -> None:
    errors = [
        diagnostic
        for diagnostic in lint_liveprog(BROKEN, HostProfile.ROOTLESS_UPSTREAM)
        if diagnostic.severity.value == "error"
    ]
    assert [(diagnostic.code, diagnostic.line) for diagnostic in errors] == [("EEL001", 12)]


def test_safe_repair_only_fixes_eel001() -> None:
    diagnostics = lint_liveprog(BROKEN, HostProfile.ROOTLESS_UPSTREAM)
    repaired = apply_safe_repairs(BROKEN, diagnostics)
    assert "spl0 = spl0 * gainLin;" in repaired
    assert len(repaired.splitlines()) == len(BROKEN.splitlines())
    assert not [
        diagnostic
        for diagnostic in lint_liveprog(repaired, HostProfile.ROOTLESS_UPSTREAM)
        if diagnostic.severity.value == "error"
    ]
