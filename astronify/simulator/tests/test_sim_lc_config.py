"""
.. module:: test_sim_lc_config
   :synopsis: Regression tests for sim_lc_config

.. moduleauthor:: Scott W. Fleming
"""

import pytest
from astronify.simulator.sim_lc_config import SimLcConfig

"""
Test cases that should return True that the SimLcConfig object has these attributes:
1.) [sim_lc_ofile, sim_lc_length, sim_lc_noise, sim_lc_visualize,
     sim_lc_yoffset, sim_lc_transit_depth, sim_lc_transit_period,
     sim_lc_transit_start, sim_lc_transit_width, sim_lc_sine_amp,
     sim_lc_sine_period, sim_lc_flare_time, sim_lc_flare_amp,
     sim_lc_flare_halfwidth]
"""


@pytest.mark.parametrize(
    "attribute",
    [
        ("sim_lc_ofile"),
        ("sim_lc_length"),
        ("sim_lc_noise"),
        ("sim_lc_visualize"),
        ("sim_lc_yoffset"),
        ("sim_lc_transit_depth"),
        ("sim_lc_transit_period"),
        ("sim_lc_transit_start"),
        ("sim_lc_transit_width"),
        ("sim_lc_sine_amp"),
        ("sim_lc_sine_period"),
        ("sim_lc_flare_time"),
        ("sim_lc_flare_amp"),
        ("sim_lc_flare_halfwidth"),
    ],
)
def test_sim_lc_config(attribute):
    assert hasattr(SimLcConfig(), attribute)
