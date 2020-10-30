"""
.. module:: sim_lc_setup_args
   :synopsis: Sets up command-line argument parser.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse
from .sim_lc_config import SimLcConfig as sim_lc_config


def sim_lc_setup_args():
    """
    Set up command-line arguments and options.

    :returns: ArgumentParser -- Stores arguments and options.
    """

    parser = argparse.ArgumentParser(
        description="Create simulated light curves, as FITS files, for use with"
        " the Astronify sonification software. Types include flat, transit, sine"
        " and flare.")

    parser.add_argument("lc_type", action="store", type=str, help="Type of light"
                        " curve to create.", choices=["flat", "transit",
                                                      "sine", "flare"])

    parser.add_argument("-o", dest="lc_ofile", action="store", type=str,
                        help="Name of output FITS file to create.",
                        default=sim_lc_config.sim_lc_ofile)

    parser.add_argument("-l", action="store", type=int,
                        default=sim_lc_config.sim_lc_length,
                        dest="lc_length", help="Total number of flux"
                        " measurements in the light curve. Default ="
                        " %(default)s.")

    parser.add_argument("-n", action="store", type=float,
                        default=sim_lc_config.sim_lc_noise,
                        dest="lc_noise", help="Amount of noise to add to the"
                        " measurements in the light curve, specified by the"
                        " standard deviation of the normal distribution to draw"
                        " from. Set to zero for no noise. Default ="
                        " %(default)s.")

    parser.add_argument("-v", action="store_true", dest="visualize",
                        default=sim_lc_config.sim_lc_vizualize,
                        help="If True, a plot of the light curve"
                        " that is generated will be plot on the screen. Default"
                        " = %(default)s.")

    parser.add_argument("-y", action="store", type=float,
                        default=sim_lc_config.sim_lc_yoffset,
                        dest="lc_yoffset", help="Baseline (unitless) flux height"
                        " of the light curve. Used to test sonification of"
                        " sources with different total brightness. Default ="
                        " %(default)s.")

    # Transit-related parameters here.
    transit_group = parser.add_argument_group("transit", "Parameters for transit"
                                              " signals.")
    transit_group.add_argument("--transit_depth", type=float,
                               default=sim_lc_config.sim_lc_transit_depth,
                               dest="transit_depth", help="Depth of the transit"
                               " signal specified as a percent, e.g., set to"
                               " 10.0 for a 10%% depth transit. Default ="
                               " %(default)s.")
    transit_group.add_argument("--transit_period", type=int,
                               default=sim_lc_config.sim_lc_transit_period,
                               dest="transit_period", help="Period of the"
                               " transit signal, specified as the number of"
                               " fluxes (bins) between the start of each event."
                               " Default = %(default)s.")
    transit_group.add_argument("--transit_start", type=int,
                               default=sim_lc_config.sim_lc_transit_start,
                               dest="transit_start", help="Start of the first"
                               " transit, specified as the index of the"
                               " flux (bin) to use as the start of the first"
                               " transit event. Default = %(default)s.")
    transit_group.add_argument("--transit_width", type=int,
                               default=sim_lc_config.sim_lc_transit_width,
                               dest="transit_width", help="Width of the"
                               " transit signal, specified as the number of"
                               " fluxes (bins) between the start and end of each"
                               " event. Default = %(default)s.")

    # Sinusoidal-related parameters here.
    sine_group = parser.add_argument_group("sinusoidal", "Parameters for"
                                           " sinusoidal signals.")
    sine_group.add_argument("--sine_amp", type=float,
                            default=sim_lc_config.sim_lc_sine_amp,
                            dest="sine_amp", help="Amplitude of the"
                            " sinusoidal signal to add. Default ="
                            " %(default)s.")
    sine_group.add_argument("--sine_period", type=float,
                            default=sim_lc_config.sim_lc_sine_period,
                            dest="sine_period", help="Period of the"
                            " sinusoidal signal, specified in the (unitless)"
                            " time axis (flux bins). Default = %(default)s.")

    # Flare-related parameters here.
    flare_group = parser.add_argument_group("flare", "Parameters for"
                                            " adding flares.")
    flare_group.add_argument("--flare_time", type=int,
                             default=sim_lc_config.sim_lc_flare_time,
                             dest="flare_time", help="Time corresponding to"
                             " the maximum flux of the flare, specified"
                             " as the index of the flux (bin) to use as"
                             " the peak time. Default = %(default)s.")
    flare_group.add_argument("--flare_amp", type=float,
                             default=sim_lc_config.sim_lc_flare_amp,
                             dest="flare_amp", help="Amplitude (maximum flux)"
                             " of the flare to add. Default = %(default)s.")
    flare_group.add_argument("--flare_halfwidth", type=int,
                             default="flare_halfwidth", help="The flare"
                             " half-width (measured in indices) that"
                             " corresponds to 't_1/2' in the Davenport et al."
                             " flare template.")

    return parser
