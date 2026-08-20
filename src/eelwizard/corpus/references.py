from __future__ import annotations

from hashlib import sha256
import re

from eelwizard.models import HostProfile, ReferenceRecord, SourceClass

EEL_VM_PIN = "284b3da00af91efc3aff6bfc1acefb4e801a8ad6"
_BOLD_SPAN_RE = re.compile(r"\*\*([^*]+)\*\*")
_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\(")


def extract_eel_vm_primitives(readme_text: str) -> list[str]:
    names: set[str] = set()
    for span in _BOLD_SPAN_RE.findall(readme_text):
        names.update(_CALL_RE.findall(span))
    return sorted(names)


def build_eel_vm_reference_records(
    readme_text: str,
    *,
    source_bytes: bytes | None = None,
    source_revision: str = EEL_VM_PIN,
) -> list[ReferenceRecord]:
    raw = source_bytes if source_bytes is not None else readme_text.encode("utf-8")
    digest = sha256(raw).hexdigest()
    return [
        ReferenceRecord(
            id=f"eel-vm:{name}",
            title=name,
            source_class=SourceClass.VM,
            host_profile=HostProfile.EEL_VM_CORE,
            source_revision=source_revision,
            source_path="readme.md",
            content_hash=digest,
            text=name,
        )
        for name in extract_eel_vm_primitives(readme_text)
    ]
