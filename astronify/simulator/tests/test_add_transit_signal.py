"""
.. module:: test_add_transit_signal
   :synopsis: Regression tests for add_transit_signal

.. moduleauthor:: Scott W. Fleming
"""

import pytest
import numpy as np
from astronify.simulator.add_transit_signal import add_transit_signal

times = np.arange(1, 101)
fluxes = np.asarray([1.0] * len(times))
all_ones = np.asarray([1.0] * len(fluxes))

# params used for below: transit_depth = 10.0, transit_period = 20,
#                        transit_start = 3, transit_width = 3
# fmt: off
transit_signal = np.asarray(
    [
        1.0, 1.0, 1.0, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.9, 0.9, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9,
        0.9, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0,
    ]
)
# fmt: om

# params used for below: transit_depth = 10.0, transit_period = 20,
#                        transit_start = -1, transit_width = 3
# fmt: off
transit_signal_negstart = np.asarray(
    [
        0.9, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.9, 0.9,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 0.9, 0.9, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.9, 0.9, 0.9, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 0.9,
    ]
)
# fmt: om

# params used for below: transit_depth = -10.0, transit_period = 20,
#                        transit_start = 3, transit_width = 3
# fmt: off
transit_signal_antitransit = np.asarray(
    [
        1.0, 1.0, 1.0, 1.1, 1.1, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.1, 1.1, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.1, 1.1, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.1, 1.1, 1.1, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.1,
        1.1, 1.1, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
        1.0, 1.0,
    ]
)
# fmt: om

"""
Test cases that result in return arrays:
1. depth, period, start, width all non-zero
2. start index is provided as a negative int
3. a negative transit depth is provided (simulate an "anti-transit")
4. transit depth equal to 0.0

Test cases that result in exceptions being thrown:
1. [TODO pending Issue #90] a zero or negative value for transit_period is submitted
2. [TODO pending Issue #90] a zero or negative value for transit_width is submitted
3. [TODO pending Issue #90] a transit width is wide enough so that one transit doesn't end before the next one should start
"""

@pytest.mark.parametrize(
    "transit_depth, transit_period, transit_start, transit_width, expected_result",
    [
        (10.0, 20, 3, 3, transit_signal),
        (10.0, 20, -1, 3, transit_signal_negstart),
        (-10.0, 20, 3, 3, transit_signal_antitransit),
        (0.0, 20, 3, 3, all_ones),
    ],
)
def test_add_transit_signal(transit_depth, transit_period, transit_start, transit_width, expected_result):
    assert np.allclose(
        add_transit_signal(fluxes, transit_depth, transit_period , transit_start, transit_width),
        expected_result,
        atol=0,
        rtol=1e-8,
        equal_nan=True,
    )
