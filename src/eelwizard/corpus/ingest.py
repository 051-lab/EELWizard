from pathlib import Path

from eelwizard.corpus.liveprog import normalize_liveprog
from eelwizard.models import HostProfile, LiveProgRecord, SourceClass

ROOTLESS_UPSTREAM_PIN = "60d25ae8a53c6f4691c090673df290a73c6b6357"


class CorpusCountError(RuntimeError):
    pass


def build_rootless_manifest(
    source_dir: Path,
    output: Path,
    expected_count: int = 40,
    primitive_catalog: set[str] | None = None,
    source_revision: str = ROOTLESS_UPSTREAM_PIN,
) -> list[LiveProgRecord]:
    paths = sorted(source_dir.glob("*.eel"), key=lambda path: path.name.casefold())
    if any(path.name.casefold() == "soloconsole.eel" for path in paths):
        raise CorpusCountError(
            "soloconsole.eel is supplemental project material, not upstream factory content"
        )
    if len(paths) != expected_count:
        raise CorpusCountError(f"expected {expected_count} upstream .eel files, found {len(paths)}")

    records = [
        normalize_liveprog(
            name=path.stem,
            text=path.read_text(encoding="utf-8"),
            source_path=path.name,
            source_class=SourceClass.SHIPPED,
            host_profile=HostProfile.ROOTLESS_UPSTREAM,
            source_revision=source_revision,
            primitive_catalog=primitive_catalog,
        )
        for path in paths
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(record.model_dump_json() + "\n" for record in records),
        encoding="utf-8",
    )
    return records
