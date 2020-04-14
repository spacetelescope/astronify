# Licensed under a 3-clause BSD style license - see LICENSE.rst

"""
Custom exceptions used in the astronify classes
"""

from astropy.utils.exceptions import AstropyWarning


class InvalidInputError(Exception):
    """
    Exception to be issued when user input is incorrect in a 
    way that prevents the function from running.
    """
    pass


class InputWarning(AstropyWarning):
    """
    Warning to be issued when user input is incorrect in
    some way but doesn't prevent the function from running.
    """
    pass
