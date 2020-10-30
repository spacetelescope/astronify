# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Data Simulation
===============

This module contains code for creating simulated/test light curves
with a variety of signals in them as either an `~astropy.table.Table`,
or FITS file. The files are designed to be read by the Astronify
software package to use when testing the sonification process.


Author: Scott W. Fleming (fleming@stsci.edu)

"""

from .sim_lc import *  # noqa: F403

__all__ = ["simulated_lc", "SimLcConfig"]  # noqa: F405
