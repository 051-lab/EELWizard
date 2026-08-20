from dataclasses import dataclass
from pathlib import Path
import subprocess
import tempfile

import numpy as np


class EelVmExecutionError(RuntimeError):
    pass


@dataclass(frozen=True)
class EelVmRunResult:
    returncode: int
    left: np.ndarray
    right: np.ndarray
    stdout: str
    stderr: str


class EelVmRunner:
    def __init__(self, executable: Path):
        self.executable = executable

    def run(self, program: str, timeout_seconds: float = 10.0) -> EelVmRunResult:
        if not self.executable.is_file():
            raise FileNotFoundError(self.executable)
        with tempfile.TemporaryDirectory(prefix="eelwizard-") as tmp:
            script = Path(tmp) / "fixture.eel"
            script.write_text(program, encoding="utf-8")
            completed = subprocess.run(
                [str(self.executable), str(script)],
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                check=False,
            )
        if completed.returncode != 0:
            raise EelVmExecutionError(
                f"EEL_VM exited {completed.returncode}: {completed.stderr or completed.stdout}"
            )

        left: list[float] = []
        right: list[float] = []
        for raw in completed.stdout.splitlines():
            if not raw.startswith("__EELWIZARD__ "):
                continue
            parts = raw.split()
            if len(parts) != 3:
                raise EelVmExecutionError(f"malformed EELWizard output: {raw}")
            left.append(float(parts[1]))
            right.append(float(parts[2]))
        if not left:
            raise EelVmExecutionError(
                "EEL_VM produced no EELWizard sentinel output; compile/runtime failure is possible"
            )
        return EelVmRunResult(
            returncode=completed.returncode,
            left=np.asarray(left, dtype=np.float64),
            right=np.asarray(right, dtype=np.float64),
            stdout=completed.stdout,
            stderr=completed.stderr,
        )
