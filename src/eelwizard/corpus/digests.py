from __future__ import annotations

import hashlib
import re

_HEADER_RE = re.compile(r"^=+\nFILE: (.+?)\n=+\n", re.MULTILINE)


def parse_repository_digest(text: str) -> dict[str, bytes]:
    """Recover source bytes from the text-digest format used by project digests.

    The digest writer places three separator newlines before each subsequent
    FILE header and two separator newlines after the final file. Those bytes
    are digest framing, not repository content.
    """
    matches = list(_HEADER_RE.finditer(text))
    files: dict[str, bytes] = {}
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[match.end() : end]
        separator = "\n\n\n" if index + 1 < len(matches) else "\n\n"
        if not content.endswith(separator):
            raise ValueError(f"digest framing missing after {match.group(1)}")
        content = content[: -len(separator)]
        files[match.group(1)] = content.encode("utf-8")
    return files


def git_blob_sha(content: bytes) -> str:
    header = f"blob {len(content)}\0".encode("ascii")
    return hashlib.sha1(header + content).hexdigest()
