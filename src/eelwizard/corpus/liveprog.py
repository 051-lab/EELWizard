from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import re

from eelwizard.corpus.annotations import annotate_liveprog
from eelwizard.models import HostProfile, LiveProgRecord, SourceClass

SECTION_RE = re.compile(r"^@([A-Za-z_][A-Za-z0-9_]*)$")
CONTROL_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):([^<]+)<([^>]*)>(.*)$")
HOST_VARIABLES = ("spl0", "spl1", "srate", "nSmps", "nCh")


@dataclass(frozen=True)
class ControlDefinition:
    name: str
    default: str
    range_spec: str
    description: str


@dataclass(frozen=True)
class LiveProgDocument:
    description: str | None
    tags: list[str]
    controls: list[ControlDefinition] = field(default_factory=list)
    sections: dict[str, str] = field(default_factory=dict)


def parse_liveprog(text: str) -> LiveProgDocument:
    description: str | None = None
    tags: list[str] = []
    controls: list[ControlDefinition] = []
    sections: dict[str, str] = {}
    current: str | None = None
    body: list[str] = []

    def flush() -> None:
        nonlocal body
        if current is not None:
            sections[current] = "\n".join(body).strip("\n")
        body = []

    for raw in text.splitlines():
        stripped = raw.strip()
        section_match = SECTION_RE.fullmatch(stripped)
        if section_match:
            flush()
            current = section_match.group(1)
            continue
        if current is not None:
            body.append(raw)
            continue
        if stripped.startswith("desc:"):
            description = stripped[5:].strip()
            continue
        if stripped.startswith("//tags:"):
            tags = [item for item in stripped[7:].strip().split() if item]
            continue
        control_match = CONTROL_RE.fullmatch(stripped)
        if control_match:
            controls.append(
                ControlDefinition(
                    name=control_match.group(1),
                    default=control_match.group(2).strip(),
                    range_spec=control_match.group(3).strip(),
                    description=control_match.group(4).strip(),
                )
            )
    flush()
    return LiveProgDocument(description=description, tags=tags, controls=controls, sections=sections)


def normalize_liveprog(
    *,
    name: str,
    text: str,
    source_path: str,
    source_class: SourceClass,
    host_profile: HostProfile,
    source_revision: str | None = None,
    primitive_catalog: set[str] | None = None,
) -> LiveProgRecord:
    doc = parse_liveprog(text)
    techniques, vm_primitives = annotate_liveprog(
        name, doc.tags, text, primitive_catalog or set()
    )
    return LiveProgRecord(
        name=name,
        source_class=source_class,
        host_profile=host_profile,
        source_path=source_path,
        source_revision=source_revision,
        content_hash=hashlib.sha256(text.encode("utf-8")).hexdigest(),
        sections=list(doc.sections),
        host_variables=[v for v in HOST_VARIABLES if re.search(rf"\b{re.escape(v)}\b", text)],
        controls=[c.name for c in doc.controls],
        tags=doc.tags,
        techniques=techniques,
        vm_primitives=vm_primitives,
        text=text,
    )
