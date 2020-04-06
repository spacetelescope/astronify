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

    parser.add_argument("-y", action="store", type=float, default=100,
                        dest="lc_yoffset", help="Baseline (unitless) flux height"
                        " of the light curve. Used to test sonification of"
                        " sources with different total brightness. Default ="
                        " %(default)s.")


    return parser
