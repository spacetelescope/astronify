"""
.. module:: test_check_flare_params
   :synopsis: Regression tests for check_flare_params

.. moduleauthor:: Scott W. Fleming
"""

import argparse
import pytest
from astronify.simulator.check_flare_params import check_flare_params

"""
Test cases that should result in an argparse.ArgumentTypeError raised:
1.) flare_time > n_fluxes
2.) flare_amplitude = 0.0
"""


@pytest.mark.parametrize(
    "n_fluxes, flare_time, flare_amp",
    [
        (10, 100, 5),
        (10, 1, 0.0),
    ],
)
def test_check_flare_params(n_fluxes, flare_time, flare_amp):
    with pytest.raises(argparse.ArgumentTypeError) as e_info:
        check_flare_params(n_fluxes, flare_time, flare_amp)
