import os
from pathlib import Path

import numpy as np
import pytest

from eelwizard.corpus.liveprog import parse_liveprog
from eelwizard.eel.runner import EelVmRunner
from eelwizard.eel.standalone import build_standalone_program


@pytest.mark.integration
def test_upstream_eel_vm_executes_gain_fixture() -> None:
    executable = os.environ.get("EELWIZARD_EEL_CLI")
    if not executable:
        pytest.skip("EELWIZARD_EEL_CLI is not configured")
    document = parse_liveprog(
        Path("tests/fixtures/upstream_gainControl.eel").read_text(encoding="utf-8")
    )
    left = np.array([0.25, -0.5, 1.0], dtype=np.float64)
    program = build_standalone_program(document, left, -left, 48000.0)
    result = EelVmRunner(Path(executable)).run(program)
    expected = left * (10 ** (-8.0 / 20.0))
    np.testing.assert_allclose(result.left, expected, rtol=2e-6, atol=2e-7)
    np.testing.assert_allclose(result.right, -expected, rtol=2e-6, atol=2e-7)
    assert result.returncode == 0
