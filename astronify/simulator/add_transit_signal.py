"""
.. module:: add_transit_signal
   :synopsis: Adds a periodic transit event to an array of fluxes.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

import numpy as np


def add_transit_signal(
    fluxes, transit_depth, transit_period, transit_start, transit_width
):
    """
    :param fluxes: Array of fluxes to add the transit signal to.
    :type fluxes: numpy.ndarray

    :param transit_depth: Depth of transit, as a percent (e.g., 10.0 = 10%.)
    :type transit_depth: float

    :param transit_period: Period of transit (number of fluxes/bins between
    the start of each event.)
    :type transit_period: int

    :param transit_start: Start index of transit (the index of the flux/bin to
    use as the start of the first transit event.)
    :type transit_start: int

    :param transit_width: Width of transit (number of fluxes/bins between
    the start and end of each event.)
    :type transit_width: int

    :returns: numpy.ndarray -- The fluxes with the transit signal added.
    """

    # Array holding the flux fractions to multiply the input flux by due to the transit.
    mod_flux_factors = np.asarray([1.0] * fluxes.size)

    # Get length of the flux array.
    n_fluxes = fluxes.size

    # Determine the indexes that should be at full transit depth.
    transit_indexes = np.zeros(n_fluxes)

    # Get the set of start indexes.
    start_indexes = np.arange(transit_start, n_fluxes + 1, transit_period, dtype=int)
    # Set transit indexes to 1.
    for st_ind in start_indexes:
        if st_ind >= 0:
            if st_ind + transit_width < fluxes.size:
                transit_indexes[st_ind : st_ind + transit_width] = 1
            else:
                transit_indexes[st_ind:] = 1
        elif st_ind > -1 * transit_width:
            # This is a negative start index that will result in a partial transit at the start.
            transit_indexes[0 : transit_width + st_ind] = 1

    # Calculate the flux fractions to multiply by to modify the fluxes due to the transit.
    mod_flux_factors[np.where(transit_indexes == 1)] = 1.0 - (transit_depth / 100.0)

    return fluxes * mod_flux_factors
