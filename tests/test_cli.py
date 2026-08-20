from typer.testing import CliRunner
from eelwizard.cli import app

runner = CliRunner()


def test_version_command() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "EELWizard 0.1.0"


def test_doctor_executes_eel_vm_smoke(tmp_path) -> None:
    executable = tmp_path / "fake-eel"
    executable.write_text(
        "#!/bin/sh\nprintf '__EELWIZARD__ 1 1\\n'\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)
    result = runner.invoke(app, ["doctor", "--eel-cli", str(executable)])
    assert result.exit_code == 0
    assert "EEL_VM executable: OK" in result.stdout
    assert "EEL_VM smoke execution: OK" in result.stdout


def test_corpus_inspect_accepts_structural_filters_without_text_query(tmp_path) -> None:
    from eelwizard.corpus.store import CorpusStore
    from eelwizard.models import HostProfile, LiveProgRecord, SourceClass

    database = tmp_path / "corpus.sqlite3"
    CorpusStore(database).rebuild(
        [
            LiveProgRecord(
                name="fractionalDelayline",
                source_class=SourceClass.SHIPPED,
                host_profile=HostProfile.ROOTLESS_UPSTREAM,
                source_path="fractionalDelayline.eel",
                content_hash="a",
                techniques=["fractional-delay"],
                vm_primitives=["fractionalDelayLineProcess"],
                text="fractionalDelayLineProcess",
            )
        ]
    )

    result = runner.invoke(
        app,
        [
            "corpus",
            "inspect",
            "--database",
            str(database),
            "--source-class",
            "SHIPPED",
            "--host-profile",
            "rootless-upstream",
            "--technique",
            "fractional-delay",
            "--vm-primitive",
            "fractionalDelayLineProcess",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert "fractionalDelayline" in result.stdout


def test_corpus_inspect_accepts_tag_filter(tmp_path) -> None:
    from eelwizard.corpus.store import CorpusStore
    from eelwizard.models import HostProfile, LiveProgRecord, SourceClass

    database = tmp_path / "tags.sqlite3"
    CorpusStore(database).rebuild(
        [
            LiveProgRecord(
                name="tagged",
                source_class=SourceClass.SHIPPED,
                host_profile=HostProfile.ROOTLESS_UPSTREAM,
                source_path="tagged.eel",
                content_hash="tagged",
                tags=["utility"],
                text="@init\n@sample",
            )
        ]
    )
    result = runner.invoke(
        app,
        ["corpus", "inspect", "--database", str(database), "--tag", "utility"],
    )
    assert result.exit_code == 0, result.stdout
    assert "tagged" in result.stdout
