"""
.. module:: sim_lc_setup_args
   :synopsis: Sets up command-line argument parser.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse

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

    parser.add_argument("lc_ofile", action="store", type=str, help="Name of"
                        " output FITS file to create.")

    parser.add_argument("-l", action="store", type=int, default=500,
                        dest="lc_length", help="Total number of flux"
                        " measurements in the light curve. Default ="
                        " %(default)s.")

    parser.add_argument("-n", action="store", type=float, default=0,
                        dest="lc_noise", help="Amount of noise to add to the"
                        " measurements in the light curve, specified by the"
                        " standard deviation of the normal distribution to draw"
                        " from. Set to zero for no noise. Default ="
                        " %(default)s.")

    parser.add_argument("-v", action="store_true", dest="visualize",
                        default=False, help="If True, a plot of the light curve"
                        " that is generated will be plot on the screen. Default"
                        " = %(default)s.")

    parser.add_argument("-y", action="store", type=float, default=100.,
                        dest="lc_yoffset", help="Baseline (unitless) flux height"
                        " of the light curve. Used to test sonification of"
                        " sources with different total brightness. Default ="
                        " %(default)s.")

    # Transit-related parameters here.
    transit_group = parser.add_argument_group("transit", "Parameters for transit"
                                              " signals.")
    transit_group.add_argument("--transit_depth", type=float, default=10.,
                               dest="transit_depth", help="Depth of the transit"
                               " signal specified as a percent, e.g., set to"
                               " 10.0 for a 10%% depth transit. Default ="
                               " %(default)s.")
    transit_group.add_argument("--transit_period", type=int, default=50,
                               dest="transit_period", help="Period of the"
                               " transit signal, specified as the number of"
                               " fluxes (bins) between the start of each event."
                               " Default = %(default)s.")
    transit_group.add_argument("--transit_start", type=int, default=10,
                               dest="transit_start", help="Start of the first"
                               " transit, specified as the index of the"
                               " flux (bin) to use as the start of the first"
                               " transit event. Default = %(default)s.")
    transit_group.add_argument("--transit_width", type=int, default=5,
                               dest="transit_width", help="Width of the"
                               " transit signal, specified as the number of"
                               " fluxes (bins) between the start and end of each"
                               " event. Default = %(default)s.")

    return parser
