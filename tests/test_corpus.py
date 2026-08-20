from pathlib import Path

import pytest

from eelwizard.corpus.ingest import CorpusCountError, build_rootless_manifest
from eelwizard.corpus.store import CorpusStore

FIXTURE = Path("tests/fixtures/upstream_gainControl.eel")


def test_wrong_upstream_count_fails(tmp_path: Path) -> None:
    src = tmp_path / "Liveprog"
    src.mkdir()
    (src / "gainControl.eel").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(CorpusCountError):
        build_rootless_manifest(src, tmp_path / "m.jsonl", expected_count=40)


def test_soloconsole_is_never_upstream_factory(tmp_path: Path) -> None:
    src = tmp_path / "Liveprog"
    src.mkdir()
    (src / "soloconsole.eel").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    with pytest.raises(CorpusCountError):
        build_rootless_manifest(src, tmp_path / "m.jsonl", expected_count=1)


def test_store_finds_shipped_gain(tmp_path: Path) -> None:
    src = tmp_path / "Liveprog"
    src.mkdir()
    (src / "gainControl.eel").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    records = build_rootless_manifest(src, tmp_path / "m.jsonl", expected_count=1)
    store = CorpusStore(tmp_path / "corpus.sqlite3")
    store.rebuild(records)
    hits = store.search_liveprog("gain spl0", limit=5)
    assert hits[0].record.name == "gainControl"
    assert hits[0].record.source_class.value == "SHIPPED"


def test_store_filters_by_technique_primitive_source_and_host(tmp_path: Path) -> None:
    from eelwizard.models import HostProfile, LiveProgRecord, SourceClass

    records = [
        LiveProgRecord(
            name="fractionalDelayline",
            source_class=SourceClass.SHIPPED,
            host_profile=HostProfile.ROOTLESS_UPSTREAM,
            source_path="fractionalDelayline.eel",
            content_hash="a",
            techniques=["fractional-delay"],
            vm_primitives=["fractionalDelayLineProcess"],
            text="fractionalDelayLineProcess",
        ),
        LiveProgRecord(
            name="vaultDelay",
            source_class=SourceClass.VAULT,
            host_profile=HostProfile.ROOTLESS_051,
            source_path="vaultDelay.eel",
            content_hash="b",
            techniques=["fractional-delay"],
            vm_primitives=["fractionalDelayLineProcess"],
            text="fractionalDelayLineProcess",
        ),
        LiveProgRecord(
            name="stftDenoise",
            source_class=SourceClass.SHIPPED,
            host_profile=HostProfile.ROOTLESS_UPSTREAM,
            source_path="stftDenoise.eel",
            content_hash="c",
            techniques=["stft"],
            vm_primitives=["stftForward", "stftBackward"],
            text="stftForward stftBackward",
        ),
    ]
    store = CorpusStore(tmp_path / "filtered.sqlite3")
    store.rebuild(records)

    delay_hits = store.search_liveprog(
        "",
        technique="fractional-delay",
        source_class=SourceClass.SHIPPED,
        host_profile=HostProfile.ROOTLESS_UPSTREAM,
    )
    assert [hit.record.name for hit in delay_hits] == ["fractionalDelayline"]

    stft_hits = store.search_liveprog(
        "",
        vm_primitive="stftForward",
        source_class=SourceClass.SHIPPED,
        host_profile=HostProfile.ROOTLESS_UPSTREAM,
    )
    assert [hit.record.name for hit in stft_hits] == ["stftDenoise"]


def test_store_text_search_remains_backward_compatible(tmp_path: Path) -> None:
    src = tmp_path / "Liveprog"
    src.mkdir()
    (src / "gainControl.eel").write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
    records = build_rootless_manifest(src, tmp_path / "m.jsonl", expected_count=1)
    store = CorpusStore(tmp_path / "compat.sqlite3")
    store.rebuild(records)
    assert store.search_liveprog("gainControl")[0].record.name == "gainControl"


def test_store_filters_by_exact_tag(tmp_path: Path) -> None:
    from eelwizard.models import HostProfile, LiveProgRecord, SourceClass

    records = [
        LiveProgRecord(
            name="tagged",
            source_class=SourceClass.SHIPPED,
            host_profile=HostProfile.ROOTLESS_UPSTREAM,
            source_path="tagged.eel",
            content_hash="tagged",
            tags=["filter", "utility"],
            text="@init\n@sample",
        ),
        LiveProgRecord(
            name="not-tagged",
            source_class=SourceClass.SHIPPED,
            host_profile=HostProfile.ROOTLESS_UPSTREAM,
            source_path="not-tagged.eel",
            content_hash="plain",
            tags=["filtering"],
            text="@init\n@sample",
        ),
    ]
    store = CorpusStore(tmp_path / "tags.sqlite3")
    store.rebuild(records)
    hits = store.search_liveprog("", tag="filter")
    assert [hit.record.name for hit in hits] == ["tagged"]


def test_text_search_does_not_drop_higher_authority_equal_match_before_rerank(tmp_path: Path) -> None:
    from eelwizard.models import HostProfile, LiveProgRecord, SourceClass

    records = [
        LiveProgRecord(
            name="vault-match",
            source_class=SourceClass.VAULT,
            host_profile=HostProfile.ROOTLESS_051,
            source_path="vault.eel",
            content_hash="v",
            text="sharedtoken",
        ),
        LiveProgRecord(
            name="shipped-match",
            source_class=SourceClass.SHIPPED,
            host_profile=HostProfile.ROOTLESS_UPSTREAM,
            source_path="shipped.eel",
            content_hash="s",
            text="sharedtoken",
        ),
    ]
    store = CorpusStore(tmp_path / "authority.sqlite3")
    store.rebuild(records)
    hits = store.search_liveprog("sharedtoken", limit=1)
    assert [hit.record.name for hit in hits] == ["shipped-match"]
