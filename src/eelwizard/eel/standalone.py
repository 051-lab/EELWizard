import math

import numpy as np

from eelwizard.corpus.liveprog import LiveProgDocument


def _aligned_region(length: int) -> int:
    base = max(16, length)
    return 1 << (base - 1).bit_length()


def _eel_float_literal(value: float) -> str:
    return np.format_float_positional(float(value), unique=True, trim="-")


def build_standalone_program(
    document: LiveProgDocument,
    left: np.ndarray,
    right: np.ndarray,
    sample_rate: float,
) -> str:
    left = np.asarray(left, dtype=np.float64)
    right = np.asarray(right, dtype=np.float64)
    if left.ndim != 1 or right.ndim != 1 or len(left) != len(right):
        raise ValueError("left/right fixtures must be equal-length 1-D arrays")
    if len(left) > 8192:
        raise ValueError("CLI-backed M0 fixtures are limited to 8192 frames")
    if not math.isfinite(sample_rate) or sample_rate <= 0:
        raise ValueError("sample_rate must be finite and positive")
    if not np.all(np.isfinite(left)) or not np.all(np.isfinite(right)):
        raise ValueError("fixtures must contain only finite values")
    if "init" not in document.sections or "sample" not in document.sections:
        raise ValueError("LiveProg requires init and sample sections")

    right_base = _aligned_region(len(left))
    lines = [
        f"srate = {_eel_float_literal(sample_rate)};",
        "inL = 0;",
        f"inR = {right_base};",
    ]
    for index, value in enumerate(left):
        lines.append(f"inL[{index}] = {_eel_float_literal(value)};")
    for index, value in enumerate(right):
        lines.append(f"inR[{index}] = {_eel_float_literal(value)};")
    lines.extend(
        [
            "",
            document.sections["init"],
            "",
            "i = 0;",
            f"loop({len(left)},",
            "  spl0 = inL[i];",
            "  spl1 = inR[i];",
        ]
    )
    lines.extend("  " + line for line in document.sections["sample"].splitlines())
    lines.extend(
        [
            '  printf("__EELWIZARD__ %.17g %.17g\\n", spl0, spl1);',
            "  i += 1;",
            ");",
            "",
        ]
    )
    return "\n".join(lines)
