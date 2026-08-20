from pathlib import Path

import numpy as np
import pytest

from eelwizard.eel.runner import EelVmExecutionError, EelVmRunner


def _make_executable(path: Path, body: str) -> Path:
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def test_runner_parses_sentinel_output(tmp_path: Path) -> None:
    executable = _make_executable(
        tmp_path / "fake-eel",
        "#!/bin/sh\nprintf '__EELWIZARD__ 0.25 -0.25\\n'\n",
    )
    result = EelVmRunner(executable).run("ignored;")
    np.testing.assert_allclose(result.left, [0.25])
    np.testing.assert_allclose(result.right, [-0.25])
    assert result.returncode == 0


def test_runner_rejects_zero_exit_without_sentinel(tmp_path: Path) -> None:
    executable = _make_executable(
        tmp_path / "fake-eel",
        "#!/bin/sh\nprintf 'syntax error near token\\n'\nexit 0\n",
    )
    with pytest.raises(EelVmExecutionError, match="no EELWizard sentinel output"):
        EelVmRunner(executable).run("bad code;")
