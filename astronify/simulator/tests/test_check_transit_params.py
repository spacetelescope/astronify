"""
.. module:: test_check_transit_params
   :synopsis: Regression tests for check_transit_params

.. moduleauthor:: Scott W. Fleming
"""

import argparse
import pytest
from astronify.simulator.check_transit_params import check_transit_params

"""
Test cases that should result in an argparse.ArgumentTypeError raised:
1.) transit_start > n_fluxes
2.) transit_width >= transit_period
"""


@pytest.mark.parametrize(
    "n_fluxes, transit_period, transit_start, transit_width",
    [
        (10, 30, 100, 5),
        (10, 3, 1, 50),
    ],
)
def test_check_transit_params(n_fluxes, transit_period, transit_start, transit_width):
    with pytest.raises(argparse.ArgumentTypeError) as e_info:
        check_transit_params(n_fluxes, transit_period, transit_start, transit_width)
