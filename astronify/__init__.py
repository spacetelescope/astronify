# Licensed under a 3-clause BSD style license - see LICENSE.rst

# Packages may add whatever they like to this file, but
# should keep this content at the top.
# ----------------------------------------------------------------------------
from ._astropy_init import *   # noqa
# ----------------------------------------------------------------------------

from .series import SoniSeries   # noqa
from .simulator.sim_lc import simulated_lc    # noqa

__all__ = ['SoniSeries', 'simulated_lc']   # noqa
