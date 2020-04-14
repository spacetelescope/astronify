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


# TODO: THIS IS SUPER BETA SOME PARTS OF IT DON'T WORK
def data_to_pitch(data_array, pitch_range=[100,10000], center_value=440, stretch='linear', minmax_percent=None, minmax_value=None):
    """
    Map data array to audible pitches
    Apply given stretch and scaling to a data array, 

    Parameters
    ----------
    pitch_range : array
        Optional. Range of acceptable pitches in Hz. Defaults to commonly stated range of human
        hearing which is 20Hz-20kHz.
    data_array : array
        The input data array.
    stretch : str
        Optional, default 'asinh'. The stretch to apply to the image array.
        Valid values are: asinh, sinh, sqrt, log, linear
    minmax_percent : array
        Optional. Interval based on a keeping a specified fraction of pixels (can be asymmetric) 
        when scaling the image. The format is [lower percentile, upper percentile], where pixel
        values below the lower percentile and above the upper percentile are clipped.
        Only one of minmax_percent and minmax_value shoul be specified.
    minmax_value : array
        Optional. Interval based on user-specified pixel values when scaling the image.
        The format is [min value, max value], where pixel values below the min value and above
        the max value are clipped.
        Only one of minmax_percent and minmax_value should be specified.

    Returns
    -------
    response : array
        The normalized data array, with values in given pitch range.
    """

    # Check for a valid stretch
    if not stretch.lower() in ('asinh', 'sinh', 'sqrt', 'log', 'linear'):
        raise InvalidInputError("Stretch {} is not supported!".format(stretch))

    # Check the scaling
    if (minmax_percent is not None) and (minmax_value is not None):
        warnings.warn("Both minmax_percent and minmax_value are set, minmax_value will be ignored.",
                      InputWarning)

    # Setting up the transform with the scaling
    if minmax_percent:
        transform = AsymmetricPercentileInterval(*minmax_percent)
    elif minmax_value:
        transform = ManualInterval(*minmax_value)
    else:  # Default, scale the entire image range to [0,1]
        transform = MinMaxInterval()
        
    # Adding the stretch to the transform
    if stretch == 'asinh':
        transform += AsinhStretch()
    elif stretch == 'sinh':
        transform += SinhStretch()
    elif stretch == 'sqrt':
        transform += SqrtStretch()
    elif stretch == 'log':
        transform += LogStretch()

   
    # Performing the transform and then putting it into the pich range
    norm_img = transform(data_array)
    
    # Want the median to be in about the middle of the human hearing range
    med = np.median(norm_img)
    norm_img = np.multiply((center_value - pitch_range[0])/med, norm_img, out=norm_img) + pitch_range[0]
    
    return norm_img
