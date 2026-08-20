from pathlib import Path

from typer.testing import CliRunner

from eelwizard.bench import RetrievalBenchmarkCase, run_retrieval_benchmark
from eelwizard.cli import app
from eelwizard.corpus.store import CorpusStore
from eelwizard.models import HostProfile, LiveProgRecord, SourceClass

runner = CliRunner()


def _store(path: Path) -> CorpusStore:
    store = CorpusStore(path)
    store.rebuild(
        [
            LiveProgRecord(
                name="gainControl",
                source_class=SourceClass.SHIPPED,
                host_profile=HostProfile.ROOTLESS_UPSTREAM,
                source_path="gainControl.eel",
                content_hash="a",
                techniques=["gain"],
                vm_primitives=["exp"],
                text="gain spl0 spl1 exp",
            ),
            LiveProgRecord(
                name="fractionalDelayline",
                source_class=SourceClass.SHIPPED,
                host_profile=HostProfile.ROOTLESS_UPSTREAM,
                source_path="fractionalDelayline.eel",
                content_hash="b",
                techniques=["fractional-delay"],
                vm_primitives=["fractionalDelayLineProcess"],
                text="fractionalDelayLineProcess spl0 spl1",
            ),
        ]
    )
    return store


def test_retrieval_benchmark_reports_pass_and_failure(tmp_path: Path) -> None:
    store = _store(tmp_path / "corpus.sqlite3")
    cases = [
        RetrievalBenchmarkCase(
            id="gain",
            query="gain spl0",
            expected_name="gainControl",
            top_k=3,
            source_class=SourceClass.SHIPPED,
            host_profile=HostProfile.ROOTLESS_UPSTREAM,
            technique="gain",
        ),
        RetrievalBenchmarkCase(
            id="missing",
            query="gain spl0",
            expected_name="not-present",
            top_k=3,
        ),
    ]

    result = run_retrieval_benchmark(store, cases)
    assert result.total == 2
    assert result.passed == 1
    assert result.pass_rate == 0.5
    assert result.cases[0].passed is True
    assert result.cases[0].hits == ["gainControl"]
    assert result.cases[1].passed is False


def test_retrieval_benchmark_cli_exits_nonzero_on_failure(tmp_path: Path) -> None:
    database = tmp_path / "corpus.sqlite3"
    _store(database)
    cases = tmp_path / "cases.json"
    report = tmp_path / "report.json"
    cases.write_text(
        '[{"id":"missing","query":"gain spl0","expected_name":"not-present","top_k":3}]',
        encoding="utf-8",
    )

    result = runner.invoke(
        app,
        [
            "benchmark",
            "retrieval",
            "--database",
            str(database),
            "--cases",
            str(cases),
            "--report",
            str(report),
        ],
    )
    assert result.exit_code == 1
    assert report.exists()
    assert '"passed": 0' in report.read_text(encoding="utf-8")
