from pathlib import Path
import json

import typer

from eelwizard import __version__
from eelwizard.bench import RetrievalBenchmarkCase, run_retrieval_benchmark
from eelwizard.corpus.ingest import build_rootless_manifest
from eelwizard.corpus.store import CorpusStore
from eelwizard.eel.runner import EelVmRunner
from eelwizard.vertical_slice import run_gain_vertical_slice
from eelwizard.models import HostProfile, LiveProgRecord, SourceClass

app = typer.Typer(no_args_is_help=True)
corpus_app = typer.Typer(no_args_is_help=True)
demo_app = typer.Typer(no_args_is_help=True)
benchmark_app = typer.Typer(no_args_is_help=True)
app.add_typer(corpus_app, name="corpus")
app.add_typer(demo_app, name="demo")
app.add_typer(benchmark_app, name="benchmark")


@app.callback()
def main() -> None:
    pass


@app.command()
def version() -> None:
    typer.echo(f"EELWizard {__version__}")


@app.command()
def doctor(eel_cli: Path = typer.Option(..., "--eel-cli")) -> None:
    runner = EelVmRunner(eel_cli)
    result = runner.run('printf("__EELWIZARD__ 1 1\\n");')
    if len(result.left) != 1 or len(result.right) != 1 or result.left[0] != 1.0 or result.right[0] != 1.0:
        raise typer.Exit(code=1)
    typer.echo("EEL_VM executable: OK")
    typer.echo("EEL_VM smoke execution: OK")


@corpus_app.command("build-rootless")
def build_rootless(
    source_dir: Path,
    output: Path = Path("corpus/generated/rootless-upstream.jsonl"),
) -> None:
    records = build_rootless_manifest(source_dir, output, expected_count=40)
    typer.echo(f"Indexed {len(records)} upstream LiveProg scripts")


@corpus_app.command("index")
def index_corpus(
    manifest: Path = Path("corpus/generated/rootless-upstream.jsonl"),
    database: Path = Path("corpus/generated/corpus.sqlite3"),
) -> None:
    records = [
        LiveProgRecord.model_validate_json(line)
        for line in manifest.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    CorpusStore(database).rebuild(records)
    typer.echo(f"Indexed {len(records)} records into {database}")


@corpus_app.command("inspect")
def inspect_corpus(
    query: str = typer.Argument(""),
    database: Path = Path("corpus/generated/corpus.sqlite3"),
    limit: int = 5,
    source_class: SourceClass | None = typer.Option(None, "--source-class"),
    host_profile: HostProfile | None = typer.Option(None, "--host-profile"),
    tag: str | None = typer.Option(None, "--tag"),
    technique: str | None = typer.Option(None, "--technique"),
    vm_primitive: str | None = typer.Option(None, "--vm-primitive"),
) -> None:
    hits = CorpusStore(database).search_liveprog(
        query,
        limit=limit,
        source_class=source_class,
        host_profile=host_profile,
        tag=tag,
        technique=technique,
        vm_primitive=vm_primitive,
    )
    for hit in hits:
        record = hit.record
        typer.echo(
            f"[{record.source_class.value}/{record.host_profile.value}] "
            f"{record.name} — {record.source_path}"
        )


@demo_app.command("gain-slice")
def demo_gain_slice(
    eel_cli: Path = typer.Option(..., "--eel-cli"),
    report: Path = typer.Option(Path("reports/gain-slice.json"), "--report"),
    database: Path = typer.Option(Path("corpus/generated/corpus.sqlite3"), "--database"),
) -> None:
    result = run_gain_vertical_slice(CorpusStore(database), EelVmRunner(eel_cli))
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    typer.echo(
        f"Source: {result.source_name} "
        f"[{result.retrieved_source_class.value}/{result.retrieved_host_profile.value}]"
    )
    typer.echo("Static validation: PASS")
    typer.echo("EEL_VM execution: PASS")
    typer.echo(f"Measured gain: {result.measured_gain_db:.2f} dB")
    typer.echo(f"Expected gain: {result.expected_gain_db:.2f} dB")
    typer.echo(f"Final status: {result.status.value}")

@benchmark_app.command("retrieval")
def benchmark_retrieval(
    database: Path = typer.Option(..., "--database"),
    cases: Path = typer.Option(..., "--cases"),
    report: Path = typer.Option(..., "--report"),
) -> None:
    raw_cases = json.loads(cases.read_text(encoding="utf-8"))
    benchmark_cases = [RetrievalBenchmarkCase.model_validate(item) for item in raw_cases]
    result = run_retrieval_benchmark(CorpusStore(database), benchmark_cases)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(result.model_dump_json(indent=2) + "\n", encoding="utf-8")
    typer.echo(f"Retrieval benchmark: {result.passed}/{result.total} ({result.pass_rate:.1%})")
    for case in result.cases:
        status = "PASS" if case.passed else "FAIL"
        typer.echo(f"{status} {case.id}: expected {case.expected_name}; hits={case.hits}")
    if not result.all_passed:
        raise typer.Exit(code=1)
