"""
.. module:: add_transit_signal
   :synopsis: Adds a periodic transit event to an array of fluxes.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

def add_transit_signal(fluxes, transit_depth, transit_period, transit_start,
                       transit_width):
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

    return fluxes
