"""
.. module:: test_add_sine_signal
   :synopsis: Regression tests for add_sine_signal

.. moduleauthor:: Scott W. Fleming
"""

import pytest
import numpy as np
from astronify.simulator.add_sine_signal import add_sine_signal

times = np.arange(1, 101)
fluxes = np.asarray([1.0] * len(times))
all_ones = np.asarray([1.0] * len(fluxes))

# params used for below: sine_amp = 1.0, sine_period = 3.0
# fmt: off
sine_signal = np.asarray(
    [
        1.8660254037844388, 0.13397459621556163, 0.9999999999999998,
        1.8660254037844393, 0.13397459621556218, 0.9999999999999996,
        1.8660254037844402, 0.1339745962155623, 0.9999999999999992,
        1.8660254037844402, 0.1339745962155624, 0.999999999999999,
        1.8660254037844404, 0.1339745962155643, 0.9999999999999988,
        1.8660254037844406, 0.1339745962155644, 0.9999999999999986,
        1.8660254037844406, 0.1339745962155645, 0.9999999999999983,
        1.8660254037844406, 0.13397459621556462, 0.999999999999998,
        1.8660254037844444, 0.13397459621556473, 0.9999999999999978,
        1.8660254037844446, 0.13397459621556496, 0.9999999999999976,
        1.866025403784441, 0.13397459621556507, 0.9999999999999902,
        1.8660254037844448, 0.13397459621556163, 0.9999999999999971,
        1.8660254037844415, 0.1339745962155653, 1.000000000000004,
        1.866025403784445, 0.13397459621556185, 0.9999999999999966,
        1.8660254037844415, 0.1339745962155655, 0.9999999999999892,
        1.8660254037844453, 0.13397459621556207, 0.9999999999999961,
        1.866025403784442, 0.13397459621557284, 1.0000000000000029,
        1.8660254037844455, 0.1339745962155694, 0.9999999999999956,
        1.866025403784442, 0.13397459621557317, 0.9999999999999882,
        1.8660254037844457, 0.13397459621556962, 0.9999999999999951,
        1.8660254037844424, 0.1339745962155663, 1.000000000000002,
        1.866025403784446, 0.13397459621557706, 0.9999999999999803,
        1.8660254037844426, 0.13397459621557362, 0.9999999999999872,
        1.8660254037844393, 0.13397459621557017, 0.9999999999999941,
        1.86602540378445, 0.13397459621556673, 1.0000000000000009,
        1.8660254037844464, 0.1339745962155775, 1.0000000000000078,
        1.866025403784443, 0.13397459621557406, 0.9999999999999862,
        1.8660254037844397, 0.13397459621557062, 0.9999999999999931,
        1.8660254037844504, 0.1339745962155673, 1.0,
        1.8660254037844468, 0.13397459621557806, 0.9999999999999785,
        1.8660254037844437, 0.13397459621557462, 0.9999999999999853,
        1.8660254037844402, 0.13397459621557117, 0.9999999999999921,
        1.8660254037844508, 0.13397459621556773, 0.999999999999999,
        1.8660254037844617,
    ]
)
# fmt: om

"""
Test cases that result in return arrays:
1. amplitude and period non-zero
2. amplitude equal to 0.0

Test cases that result in exceptions being thrown:
1. [TODO pending Issue #89] a negative value for sine_amp is submitted
2. [TODO pending Issue #89] a zero or negative value for sine_period is submitted
"""

def test_add_sine_signal_nonzero():
    assert np.allclose(
        add_sine_signal(times, fluxes, 1.0, 3.0),
        sine_signal,
        atol=0,
        rtol=1e-8,
        equal_nan=True,
    )

def test_add_sine_signal_zeroamp():
    assert np.array_equal(
        add_sine_signal(times, fluxes, 0.0, 1.0),
        all_ones,
    )
