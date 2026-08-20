from pathlib import Path

import numpy as np

from eelwizard.corpus.ingest import build_rootless_manifest
from eelwizard.corpus.store import CorpusStore
from eelwizard.eel.runner import EelVmRunResult
from eelwizard.models import ProjectStatus, SourceClass
from eelwizard.vertical_slice import run_gain_vertical_slice


class FakeRunner:
    def __init__(self, frame_count: int = 4800):
        time = np.arange(frame_count, dtype=np.float64) / 48000.0
        source = 0.5 * np.sin(2.0 * np.pi * 997.0 * time)
        self.output = source * (10 ** (-8.0 / 20.0))

    def run(self, program: str) -> EelVmRunResult:
        return EelVmRunResult(0, self.output, self.output, "", "")


def test_vertical_slice_reaches_measurement_pass(tmp_path: Path) -> None:
    source = tmp_path / "Liveprog"
    source.mkdir()
    fixture = Path("tests/fixtures/upstream_gainControl.eel").read_text(encoding="utf-8")
    (source / "gainControl.eel").write_text(fixture, encoding="utf-8")
    records = build_rootless_manifest(source, tmp_path / "m.jsonl", expected_count=1)
    store = CorpusStore(tmp_path / "corpus.sqlite3")
    store.rebuild(records)
    report = run_gain_vertical_slice(store, FakeRunner())
    assert report.source_name == "gainControl"
    assert report.retrieved_source_class is SourceClass.SHIPPED
    assert report.status is ProjectStatus.MEASUREMENT_PASS
    assert any(diagnostic.code == "EEL001" for diagnostic in report.diagnostics_before)
    assert not [
        diagnostic
        for diagnostic in report.diagnostics_after
        if diagnostic.severity.value == "error"
    ]
    assert abs(report.measured_gain_db + 8.0) < 0.02
