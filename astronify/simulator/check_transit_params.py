"""
.. module:: check_transit_params
   :synopsis: Performs checks on transit parameters to make sure the values
       are self-consistent (start index isn't larger than the length of the
       array, duration isn't longer than the period, etc.)

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse


def check_transit_params(n_fluxes, transit_period, transit_start, transit_width):
    """
    :param n_fluxes: Number of fluxes in the light curve.
    :type n_fluxes: int

    :param transit_period: Period of transit (number of fluxes/bins between
    the start of each event.)
    :type transit_period: int

    :param transit_start: Start index of transit (the index of the flux/bin to
    use as the start of the first transit event.)
    :type transit_start: int

    :param transit_width: Width of transit (number of fluxes/bins between
    the start and end of each event.)
    :type transit_width: int
    """

    # Start index must be less than total numbr of fluxes.
    if transit_start > n_fluxes:
        raise argparse.ArgumentTypeError("The transit start must be less than"
                                         " the total number of fluxes in the"
                                         " simulated light curve."
                                         " Number of fluxes = " + str(n_fluxes) +
                                         ", start index requested is " +
                                         str(transit_start) + ".")

    # The start index must be greater than or equal to zero.
    if transit_start < 0:
        raise argparse.ArgumentTypeError("The transit start must be greater than"
                                         " or equal to zero, start"
                                         " index requested is " +
                                         str(transit_start) + ".")

    # The transit period must be greater than the transit duration (width).
    if transit_width >= transit_period:
        raise argparse.ArgumentTypeError("Transit duration must be less than"
                                         " the transit period. Requested"
                                         " transit duration = " +
                                         str(transit_width) + ", requested"
                                         " transit period = " +
                                         str(transit_period) + ".")
