"""
.. module:: add_sine_signal
   :synopsis: Adds a sinusoidal signal to an array of fluxes.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

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
    sine_signal = Sine1D(amplitude=sine_amp, frequency=1./sine_period)

    fluxes += sine_signal(times)

    return fluxes
