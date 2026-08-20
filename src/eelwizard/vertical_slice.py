from typing import Protocol

from pydantic import BaseModel

from eelwizard.corpus.liveprog import parse_liveprog
from eelwizard.corpus.store import CorpusStore
from eelwizard.eel.lint import lint_liveprog
from eelwizard.eel.repair import apply_safe_repairs
from eelwizard.eel.runner import EelVmRunResult
from eelwizard.eel.standalone import build_standalone_program
from eelwizard.lab.measurements import measure_gain_db
from eelwizard.lab.signals import stereo_sine
from eelwizard.models import (
    Diagnostic,
    HostProfile,
    ProjectStatus,
    SourceClass,
)


class VerticalSliceError(RuntimeError):
    pass


class Runner(Protocol):
    def run(self, program: str) -> EelVmRunResult:
        ...


class VerticalSliceReport(BaseModel):
    source_name: str
    retrieved_source_class: SourceClass
    retrieved_host_profile: HostProfile
    diagnostics_before: list[Diagnostic]
    diagnostics_after: list[Diagnostic]
    status: ProjectStatus
    measured_gain_db: float
    expected_gain_db: float
    gain_error_db: float
    eel_vm_returncode: int


def run_gain_vertical_slice(store: CorpusStore, runner: Runner) -> VerticalSliceReport:
    hits = store.search_liveprog("gain spl0", limit=5)
    if not hits:
        raise VerticalSliceError("gainControl was not retrieved")
    hit = next((item for item in hits if item.record.name == "gainControl"), None)
    if (
        hit is None
        or hit.record.source_class is not SourceClass.SHIPPED
        or hit.record.host_profile is not HostProfile.ROOTLESS_UPSTREAM
    ):
        raise VerticalSliceError(
            "gainControl must come from SHIPPED/rootless-upstream corpus"
        )

    broken = hit.record.text.replace(
        "spl0 = spl0 * gainLin;",
        "spl0 = spl0 * gainLin",
        1,
    )
    if broken == hit.record.text:
        raise VerticalSliceError("controlled defect could not be introduced")
    before = lint_liveprog(broken, HostProfile.ROOTLESS_UPSTREAM)
    repaired = apply_safe_repairs(broken, before)
    after = lint_liveprog(repaired, HostProfile.ROOTLESS_UPSTREAM)
    if [diagnostic for diagnostic in after if diagnostic.severity.value == "error"]:
        raise VerticalSliceError("static validation failed after safe repair")

    left, right = stereo_sine(997.0, 48000.0, 0.1, 0.5)
    program = build_standalone_program(
        parse_liveprog(repaired),
        left,
        right,
        48000.0,
    )
    result = runner.run(program)
    if result.returncode != 0:
        raise VerticalSliceError("EEL_VM execution failed")
    measured = measure_gain_db(left, result.left)
    expected = -8.0
    error = measured - expected
    if abs(error) > 0.02:
        raise VerticalSliceError(f"gain error {error:.6f} dB exceeds 0.02 dB")
    return VerticalSliceReport(
        source_name=hit.record.name,
        retrieved_source_class=hit.record.source_class,
        retrieved_host_profile=hit.record.host_profile,
        diagnostics_before=before,
        diagnostics_after=after,
        status=ProjectStatus.MEASUREMENT_PASS,
        measured_gain_db=measured,
        expected_gain_db=expected,
        gain_error_db=error,
        eel_vm_returncode=result.returncode,
    )
