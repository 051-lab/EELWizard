import numpy as np

from eelwizard.lab.measurements import measure_gain_db
from eelwizard.lab.signals import stereo_sine


def test_minus_8_db_measurement() -> None:
    left, right = stereo_sine(997.0, 48000.0, 0.1, 0.5)
    assert np.array_equal(left, right)
    processed = left * (10 ** (-8.0 / 20.0))
    assert abs(measure_gain_db(left, processed) + 8.0) < 1e-9


def test_silent_reference_is_rejected() -> None:
    with np.testing.assert_raises(ValueError):
        measure_gain_db(np.zeros(8), np.zeros(8))
