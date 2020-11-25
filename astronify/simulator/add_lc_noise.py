"""
.. module:: add_lc_noise
   :synopsis: Adds Gaussian noise of a specified width to an array of fluxes.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import numpy as np


def add_lc_noise(fluxes, lc_noise):
    """
    :param fluxes: Array of fluxes to add noise to.
    :type fluxes: numpy.ndarray

    :param lc_noise: Standard deviation of normal distribution to draw from when
    adding noise, a value of zero means no noise is added.
    :type lc_noise: float

    :returns: numpy.ndarray -- The fluxes after being adjusted by the noise.
    """

    noise = np.random.normal(0, lc_noise, len(fluxes))

    return fluxes + noise
