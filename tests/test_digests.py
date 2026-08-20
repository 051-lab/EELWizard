import hashlib
from pathlib import Path

from eelwizard.corpus.digests import git_blob_sha, parse_repository_digest


def test_parse_repository_digest_excludes_digest_separators() -> None:
    text = (
        "Directory structure:\n"
        "================================\nFILE: one.txt\n================================\n"
        "alpha\n\n\n\n"
        "================================\nFILE: two.txt\n================================\n"
        "beta\n\n\n"
    )
    files = parse_repository_digest(text)
    assert files["one.txt"] == b"alpha\n"
    assert files["two.txt"] == b"beta\n"


def test_pinned_digest_reproduces_loose_eel_git_blob() -> None:
    digest = Path("/mnt/data/EEL_VM_digest.txt").read_text(encoding="utf-8")
    files = parse_repository_digest(digest)
    loose = files["loose_eel.c"]
    assert len(loose) == 4979
    assert git_blob_sha(loose) == "767d91549cb3bb059c8bdd987f425e9a85b288bf"
