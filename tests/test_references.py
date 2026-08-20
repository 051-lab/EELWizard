from hashlib import sha256
from pathlib import Path

from eelwizard.corpus.digests import parse_repository_digest
from eelwizard.corpus.references import (
    EEL_VM_PIN,
    build_eel_vm_reference_records,
    extract_eel_vm_primitives,
)
from eelwizard.models import HostProfile, SourceClass


def test_extract_eel_vm_primitives_from_documented_calls() -> None:
    text = """
- **fft(start_index, size), ifft(start_index, size)**
- **fractionalDelayLineProcess(start_index, xn)**
- **FIRInit(start_index, hLen)**
- **FIRProcess(start_index, xn, coefficients)**
- **Conv1DProcess(start_index, x1, x2)**
- **IIRBandSplitterProcess(start_index, xn, band1, band2)**
"""
    assert extract_eel_vm_primitives(text) == [
        "Conv1DProcess",
        "FIRInit",
        "FIRProcess",
        "IIRBandSplitterProcess",
        "fft",
        "fractionalDelayLineProcess",
        "ifft",
    ]


def test_real_eel_vm_readme_builds_pinned_vm_reference_records() -> None:
    digest = Path("/mnt/data/EEL_VM_digest.txt").read_text(encoding="utf-8")
    readme = parse_repository_digest(digest)["readme.md"]
    text = readme.decode("utf-8")
    primitives = extract_eel_vm_primitives(text)
    for required in (
        "fft",
        "ifft",
        "fractionalDelayLineProcess",
        "FIRInit",
        "FIRProcess",
        "Conv1DProcess",
        "IIRBandSplitterProcess",
    ):
        assert required in primitives

    records = build_eel_vm_reference_records(text, source_bytes=readme)
    fft = next(record for record in records if record.title == "fft")
    assert fft.source_class is SourceClass.VM
    assert fft.host_profile is HostProfile.EEL_VM_CORE
    assert fft.source_revision == EEL_VM_PIN
    assert fft.source_path == "readme.md"
    assert fft.content_hash == sha256(readme).hexdigest()
