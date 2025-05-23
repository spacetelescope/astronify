"""
.. module:: add_sine_signal
   :synopsis: Adds a sinusoidal signal to an array of fluxes.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import numpy as np
import warnings
from astronify.utils.exceptions import InputWarning
from astropy.modeling.models import Sine1D


def add_sine_signal(times, fluxes, sine_amp, sine_period):
    """
    :param times: Array of (unitless) times (flux bins) associated with the
    fluxes.
    :type times: numpy.ndarray

    :param fluxes: Array of fluxes to add the sinusoidal signal to.
    :type fluxes: numpy.ndarray

    :param sine_amp: Amplitude of the sinusoidal signal to add.
    :type sine_anp: float

    :param sine_period: Period of the sinusoidal signal to add.
    :type sine_period: float

    :returns: numpy.ndarray -- The fluxes with the sinusoidal signal added.
    """

    # Generate sinusoidal signal.
    if sine_amp > 0.0:
        sine_signal = Sine1D(amplitude=sine_amp, frequency=1.0 / sine_period)
        fluxes_to_add = sine_signal(times)
    elif sine_amp == 0.0:
        warnings.warn(
            "Warning: requested to add a single signal of zero amplitude.", InputWarning
        )
        fluxes_to_add = np.asarray([0.0] * fluxes.size)

    return fluxes + fluxes_to_add
