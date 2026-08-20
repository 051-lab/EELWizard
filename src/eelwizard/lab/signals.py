import math

import numpy as np


def stereo_sine(
    frequency: float,
    sample_rate: float,
    duration_seconds: float,
    amplitude: float,
) -> tuple[np.ndarray, np.ndarray]:
    frame_count = round(sample_rate * duration_seconds)
    time = np.arange(frame_count, dtype=np.float64) / sample_rate
    mono = amplitude * np.sin(2.0 * math.pi * frequency * time)
    return mono.copy(), mono.copy()
