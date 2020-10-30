"""
.. module:: add_flare_signal
   :synopsis: Adds a flare event to an array of fluxes.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import numpy as np


def add_flare_signal(fluxes, flare_time, flare_amp, flare_halfwidth):
    """
    Model is based on Davenport et al.
    (https://ui.adsabs.harvard.edu/abs/2014ApJ...797..122D/abstract)

    F_rise = 1 + 1.941(t) - 0.175(t^2) - 2.246(t^3) - 1.125(t^4)
    where t = time at half the maximum flux, after normalizing such that
    the flux at t=0 is the peak of the flare.

    F_decay = 0.6890*e^(-1.600*t) + 0.3030*e^(-0.2783*t)
    where t = time at half the maximum flux, after normalizing such that
    the flux at t=0 is the peak of the flare.

    :param fluxes: Array of fluxes to add the flare signal to.
    :type fluxes: numpy.ndarray

    :param flare_time: Time corresponding to the maximum flare flux.
    :type flare_time: int

    :param flare_amp: The peak (maximum flux) of the flare.
    :type flare_amp: float

    :param flare_halfwidth: The flare half-width (measured in indices) that
    corresponds to "t_1/2" in the Davenport et al. flare template.
    :type flare_halfwidth: index

    :returns: numpy.ndarray -- The fluxes with the flare signal added.
    """

    # This array will contain the fluxes of the flare to add to the input.
    fluxes_to_add = np.zeros(fluxes.shape[0])

    # We must be careful if the flare_halfwidth pushes us past the zero'th
    # index though.  If it does, we temporarily prepend some extra indices.
    truncated_start = flare_time - flare_halfwidth < 0
    if truncated_start:
        n_to_add_rise = abs(flare_time - flare_halfwidth + 1)
        fluxes_to_add = np.concatenate([np.zeros(n_to_add_rise), fluxes_to_add])
        # Need to move the 'flare_time' index over now...
        flare_time += n_to_add_rise

    # Where "n" = 6 in Davenport et al., where the decay phase is defined from
    # t_1/2 = [0,6], but we will choose to extend to the end of the light curve
    # so that the decay gets as close to zero as possible.
    n_t12 = int((fluxes_to_add.shape[0] + 1 - flare_time)/flare_halfwidth)

    # Create the normalized part of the rise time.
    # In the Davenport et al. flare template, the rise part of the flare
    # is defined from a region extending from -1 * "t_1/2" (defined here as
    # 'flare_halfwidth') out to 't_1/2' = 0, which is the peak of the flare
    # (defined here as  'flare_time'.
    # Therefore, we use Davenport et al. Eqn. 1 to set the RISE fluxes
    # between 'flare_time-flare_halfwidth' and 'flare_time' indices.
    #
    # If we want a flare halfwidth of 4 indices, we need to make a linear step
    # array from -1. to 0. that is 'halfwidth' in length, e.g.:
    #   [-1, -0.6667, -0.3333, 0.]
    # Then apply Davenport et al. Eqn. 1 to this array (now expressed in "t_1/2")
    #   Eqn. 1 * [-1, -0.6667, -0.3333, 0.]
    # Then we insert these fluxes into the array at indices:
    #  [flare_time-flare_halfwidth+1 : flare_time]

    # Generate indices in "t_1/2" units.
    t12_rise_indices = np.linspace(-1., 0., flare_halfwidth)
    # Compute fluxes for the rise part.
    rise_fluxes = (1. + 1.941*t12_rise_indices - 0.175*t12_rise_indices**2. -
                   2.246*t12_rise_indices**3. - 1.125*t12_rise_indices**4.)
    # Insert these fluxes into the correct location in our light curve.
    fluxes_to_add[flare_time-flare_halfwidth+1:flare_time+1] = rise_fluxes

    # Create the normalized part of the decay time.
    # In Davenport et al., they define their Eqn. 4 from t_1/2 = [0, 6].
    #
    # If our halfwidth is 4 indices, then make a linear step array "n"*halfwidth
    # Davenport et al. defined the decay from [0, 6], so n=6 in their case...
    #  [0., 0.26086957, 0.52173913, ... , 5.47826087, 5.73913043, 6.]
    # Then apply Davenport Eqn. 4 to this array expressed in "t_1/2"
    #  Eqn. 4 * [0., 0.26086957, 0.52173913, ... , 5.47826087, 5.73913043, 6.]
    #
    # Then we insert these fluxes into the array of indices:
    #  [flare_time : flare_time + n*flare_halfwidth-1

    # Generate indices in "t_1/2" units.
    t12_decay_indices = np.linspace(0., n_t12, n_t12*flare_halfwidth)
    
    # Compute fluxes for the decay part.
    decay_fluxes = (0.6890*np.exp(-1.600*t12_decay_indices) +
                    0.3030*np.exp(-0.2783*t12_decay_indices))
    
    # Insert these fluxes into the correct location in our light curve.
    # Note: the above index range is correct, but in Python you need to go one
    # extra when slicing, hence 6*flare_halfwidth-1+1 = 6*flare_halfwidth...
    fluxes_to_add[flare_time: flare_time+n_t12*flare_halfwidth] = decay_fluxes

    # Scale the fluxes to add (which are normalized at this point) by 'flare_amp'
    fluxes_to_add *= flare_amp

    # If we needed to add some filler indices in the beginning, remove them now.
    if truncated_start:
        fluxes_to_add = fluxes_to_add[n_to_add_rise:]

    return fluxes + fluxes_to_add
