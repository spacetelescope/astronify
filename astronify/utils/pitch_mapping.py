# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Pitch mapping functionality
===========================

Functionality for taking arbitrary data values to audible pitches.
"""

import warnings

import numpy as np

from astropy.visualization import (SqrtStretch, LogStretch, AsinhStretch, SinhStretch, LinearStretch,
                                   MinMaxInterval, ManualInterval, AsymmetricPercentileInterval)

from .exceptions import InputWarning, InvalidInputError

__all__ = ['data_to_pitch']


def data_to_pitch(data_array, pitch_range=[100,10000], center_pitch=440, zero_point="median",
                  stretch='linear', minmax_percent=None, minmax_value=None):
    """
    Map data array to audible pitches in the given range, and apply stretch and scaling
    as required.

    Parameters
    ----------
    data_array : array-like
        Data to map to pitch values. Individual data values should be floats.
    pitch_range : array
        Optional, default [100,10000]. Range of acceptable pitches in Hz. 
    center_pitch : float
        Optional, default 440. The pitch in Hz where that the the zero point of the 
        data will be mapped to.
    zero_point : str or float
        Optional, default "median". The data value that will be mapped to the center
        pitch. Options are mean, median, or a specifical data value (float).
    stretch : str
        Optional, default 'linear'. The stretch to apply to the data array.
        Valid values are: asinh, sinh, sqrt, log, linear
    minmax_percent : array
        Optional. Interval based on a keeping a specified fraction of data values (can be asymmetric) 
        when scaling the data. The format is [lower percentile, upper percentile], where data
        values below the lower percentile and above the upper percentile are clipped.
        Only one of minmax_percent and minmax_value should be specified.
    minmax_value : array
        Optional. Interval based on user-specified data values when scaling the data array.
        The format is [min value, max value], where data values below the min value and above
        the max value are clipped.
        Only one of minmax_percent and minmax_value should be specified.

    Returns
    -------
    response : array
        The normalized data array, with values in given pitch range.
    """

    # Parsing the zero point
    if zero_point in ("med", "median"):
        zero_point = np.median(data_array)
    if zero_point in ("ave", "mean", "average"):
        zero_point = np.mean(data_array)

    if (data_array == zero_point).all(): # All values are the same, no more calculation needed
        return np.full(len(data_array), zero_point) 

    # Normalizing the data_array and adding the zero point (so it can go through the same transform)
    data_array = np.append(np.array(data_array), zero_point)

    # Setting up the transform with the stretch
    if stretch == 'asinh':
        transform = AsinhStretch()
    elif stretch == 'sinh':
        transform = SinhStretch()
    elif stretch == 'sqrt':
        transform = SqrtStretch()
    elif stretch == 'log':
        transform = LogStretch()
    elif stretch == 'linear':
        transform = LinearStretch()
    else:
        raise InvalidInputError("Stretch {} is not supported!".format(stretch))

    # Adding the scaling to the transform
    if minmax_percent is not None:
        transform += AsymmetricPercentileInterval(*minmax_percent)
        
        if minmax_value is not None:
            warnings.warn("Both minmax_percent and minmax_value are set, minmax_value will be ignored.",
                          InputWarning)
    elif minmax_value is not None:
        transform += ManualInterval(*minmax_value)
    else:  # Default, scale the entire image range to [0,1]
        transform += MinMaxInterval()
   
    # Performing the transform and then putting it into the pich range
    pitch_array = transform(data_array)

    zero_point = pitch_array[-1]
    pitch_array = pitch_array[:-1]
    
    pitch_array = np.multiply((center_pitch - pitch_range[0])/zero_point, pitch_array, out=pitch_array) + pitch_range[0]
    
    return pitch_array

