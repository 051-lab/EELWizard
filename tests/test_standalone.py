from pathlib import Path

import numpy as np

from eelwizard.corpus.liveprog import parse_liveprog
from eelwizard.eel.standalone import build_standalone_program


def test_standalone_contains_only_vm_code() -> None:
    document = parse_liveprog(
        Path("tests/fixtures/upstream_gainControl.eel").read_text(encoding="utf-8")
    )
    program = build_standalone_program(
        document,
        np.array([0.25, -0.5, 1.0]),
        np.array([-0.25, 0.5, -1.0]),
        48000.0,
    )
    assert "desc:" not in program
    assert "@init" not in program
    assert "@sample" not in program
    assert program.count("gainLin = exp") == 1
    assert "loop(3," in program
    assert "__EELWIZARD__" in program


def test_standalone_rejects_nonfinite_fixture() -> None:
    document = parse_liveprog(
        Path("tests/fixtures/upstream_gainControl.eel").read_text(encoding="utf-8")
    )
    with np.testing.assert_raises(ValueError):
        build_standalone_program(
            document,
            np.array([np.nan]),
            np.array([0.0]),
            48000.0,
        )


def test_standalone_uses_positional_float_literals_for_small_values() -> None:
    document = parse_liveprog(
        Path("tests/fixtures/upstream_gainControl.eel").read_text(encoding="utf-8")
    )
    program = build_standalone_program(
        document,
        np.array([6.544984675218362e-05]),
        np.array([6.544984675218362e-05]),
        48000.0,
    )
    assignment_lines = [line for line in program.splitlines() if line.startswith(("inL[", "inR["))]
    assert assignment_lines
    assert all("e-" not in line.lower() and "e+" not in line.lower() for line in assignment_lines)
    assert "0.00006544984675218362" in program
