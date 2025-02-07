"""
.. module:: test_add_lc_noise
   :synopsis: Regression tests for add_lc_noise

.. moduleauthor:: Scott W. Fleming
"""

import pytest
import numpy as np
from astronify.simulator.add_lc_noise import add_lc_noise

fluxes = np.asarray([1.0] * 100)
all_ones = np.asarray([1.0] * len(fluxes))

"""
Test cases that result in return arrays:
1. lc_noise = 0.0
2. lc_noise = 4.0

Note that, since this is randomly generated noise, the non-zero test just
verifies not all fluxes are at the original flux value of 1.0. One could
consider defining a test such that all fluxes are within the expected standard
deviation of the input value, but that seems too much.

Test cases that result in exceptions being thrown:
1. [TODO pending Issue #86] a negative value for lc_noise is submitted
"""


def test_add_lc_noise_zero():
    assert np.array_equal(
        add_lc_noise(fluxes, 0.0),
        all_ones,
    )


def test_add_lc_noise_nonzero():
    assert not np.array_equal(
        add_lc_noise(fluxes, 4.0),
        all_ones,
    )
