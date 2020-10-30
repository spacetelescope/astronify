"""
.. module:: check_flare_params
   :synopsis: Performs checks on flare parameters to make sure the values
       are self-consistent (start index isn't larger than the length of the
       array, amplitude is not negative, etc.)

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import argparse


def check_flare_params(n_fluxes, flare_time, flare_amp):
    """
    :param n_fluxes: Number of fluxes in the light curve.
    :type n_fluxes: int

    :param flare_time: Time corresponding to the maximum flare flux.
    :type flare_time: int

    :param flare_amp: The peak (maximum flux) of the flare.
    :type flare_amp: float
    """

    # Flare time index must be less than total numbr of fluxes.
    if flare_time > n_fluxes:
        raise argparse.ArgumentTypeError("The flare time at peak flux must be"
                                         " less than the total number of fluxes"
                                         " in the simulated light curve."
                                         " Number of fluxes = " + str(n_fluxes) +
                                         ", flare time requested is " +
                                         str(flare_time) + ".")

    # Flare time index must be greater than or equal to zero.
    if flare_time < 0:
        raise argparse.ArgumentTypeError("The flare time at peak flux must be"
                                         " greater than or equal to zero, flare"
                                         " time requested is " +
                                         str(flare_time) + ".")

    # The flare amplitude must be greater than zero.
    if flare_amp <= 0.:
        raise argparse.ArgumentTypeError("Flare amplitude must be greater than"
                                         " zero. Requested"
                                         " flare amplitude = " +
                                         str(flare_amp) + ".")
