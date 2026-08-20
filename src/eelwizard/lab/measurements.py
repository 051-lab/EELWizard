import math

import numpy as np


def measure_gain_db(reference: np.ndarray, processed: np.ndarray) -> float:
    reference = np.asarray(reference, dtype=np.float64)
    processed = np.asarray(processed, dtype=np.float64)
    if reference.shape != processed.shape:
        raise ValueError("reference and processed arrays must have equal shape")
    ref_rms = float(np.sqrt(np.mean(np.square(reference))))
    out_rms = float(np.sqrt(np.mean(np.square(processed))))
    if ref_rms == 0.0:
        raise ValueError("reference signal is silent")
    if out_rms == 0.0:
        return float("-inf")
    return 20.0 * math.log10(out_rms / ref_rms)
