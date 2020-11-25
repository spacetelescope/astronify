import pytest
import numpy as np

from ..pitch_mapping import data_to_pitch
from ..exceptions import InputWarning, InvalidInputError


def test_data_to_pitch():
    """
    Testing data_to_pitch function.
    """

    # Simplifying output
    pitch_range = [400, 500]
    center_pitch = 450

    # basic linear stretch
    data_arr = np.array([[1, 0, .25, .75]])
    pitch_arr = data_arr*(pitch_range[1]-pitch_range[0]) + pitch_range[0]
    
    assert (pitch_arr == data_to_pitch(data_arr, pitch_range, center_pitch,
                                       stretch='linear')).all()
    # invert
    pitch_arr = pitch_range[1] - data_arr*(pitch_range[1]-pitch_range[0])
    assert (pitch_arr == data_to_pitch(data_arr, pitch_range, center_pitch,
                                       stretch='linear', invert=True)).all()

    # linear stretch where input image must be scaled 
    data_arr = np.array([10, 20, 12.5, 17.5])
    pitch_arr = ((data_arr - data_arr.min())/(data_arr.max()-data_arr.min()) *
                 (pitch_range[1]-pitch_range[0])) + pitch_range[0]
    assert (pitch_arr == data_to_pitch(data_arr, pitch_range, center_pitch,
                                       stretch='linear')).all()

    # linear stretch with non-equal lower/upper pitch ranges
    data_arr = np.array([[1, 0, .25, .75]])
    pitch_arr = data_arr*(pitch_range[1]-pitch_range[0]) + pitch_range[0]

    pitch_range = [300, 500]
    assert (pitch_arr == data_to_pitch(data_arr, [300, 500],
                                       center_pitch, stretch='linear')).all()
    pitch_range = [400, 600]
    assert (pitch_arr == data_to_pitch(data_arr, [400, 600],
                                       center_pitch, stretch='linear')).all()
    pitch_range = [400, 500]
    
    # min_max val
    minval, maxval = 0, 1
    data_arr = np.array([1, 0, -1, 2])
    pitch_arr = data_to_pitch(data_arr, pitch_range, center_pitch,
                              stretch='linear', minmax_value=[minval, maxval])
    data_arr[data_arr < minval] = minval
    data_arr[data_arr > maxval] = maxval
    manual_pitch_arr = data_arr*(pitch_range[1]-pitch_range[0]) + pitch_range[0]
    assert (manual_pitch_arr == pitch_arr).all()

    minval, maxval = 0, 1
    data_arr = np.array([1, 0, .25, .75])
    pitch_arr = data_to_pitch(data_arr, pitch_range, center_pitch,
                              stretch='linear', minmax_value=[minval, maxval])
    data_arr[data_arr < minval] = minval
    data_arr[data_arr > maxval] = maxval
    manual_pitch_arr = data_arr*(pitch_range[1]-pitch_range[0]) + pitch_range[0]
    assert (manual_pitch_arr == pitch_arr).all()

    # min_max percent
    data_arr = np.array([1.1, -0.1, 1, 0, .25, .75])
    pitch_arr = data_to_pitch(data_arr, pitch_range, center_pitch,
                              stretch='linear', minmax_percent=[20, 80])
    assert (np.isclose(pitch_arr, np.array([500, 400, 500, 400,
                                            422.22222222, 477.77777778]))).all()

    # asinh
    data_arr = np.array([1, 0, .25, .75])
    zero_point = 0.21271901209248895
    pitch_arr = data_to_pitch(data_arr, pitch_range, center_pitch, zero_point, stretch='asinh')
    manual_pitch_arr = np.arcsinh(data_arr*10)/np.arcsinh(10)*(pitch_range[1]-pitch_range[0]) + pitch_range[0]
    assert (manual_pitch_arr == pitch_arr).all()

    # sinh
    data_arr = np.array([1, 0, .25, .75])
    zero_point = 0.7713965391706435
    pitch_arr = data_to_pitch(data_arr, pitch_range, center_pitch, zero_point, stretch='sinh')
    manual_pitch_arr = np.sinh(data_arr*3)/np.sinh(3)*(pitch_range[1]-pitch_range[0]) + pitch_range[0]
    assert (manual_pitch_arr == pitch_arr).all()

    # sqrt
    data_arr = np.array([1, 0, .25, .75])
    zero_point = 0.25
    pitch_arr = data_to_pitch(data_arr, pitch_range, center_pitch, zero_point, stretch='sqrt')
    manual_pitch_arr = np.sqrt(data_arr)*(pitch_range[1]-pitch_range[0]) + pitch_range[0]
    assert (manual_pitch_arr == pitch_arr).all()

    # log
    data_arr = np.array([1, 0, .25, .75])
    zero_point = 0.030638584039112748
    pitch_arr = data_to_pitch(data_arr, pitch_range, center_pitch, zero_point, stretch='log')
    manual_pitch_arr = np.log(1000*data_arr+1)/np.log(1001)*(pitch_range[1]-pitch_range[0]) + pitch_range[0]
    assert (manual_pitch_arr == pitch_arr).all()

    # Bad stretch
    with pytest.raises(InvalidInputError):
        data_arr = np.array([1, 0, .25, .75])
        data_to_pitch(data_arr, stretch='lin')

    # Giving both minmax percent and cut
    data_arr = np.array([1.1, -0.1, 1, 0, .25, .75])
    pitch_arr = data_to_pitch(data_arr, pitch_range, center_pitch, stretch='linear', minmax_percent=[20, 80])
    with pytest.warns(InputWarning):
        test_arr = data_to_pitch(data_arr, pitch_range, center_pitch, stretch='linear',  
                                 minmax_value=[0, 1], minmax_percent=[20, 80])
    assert (pitch_arr == test_arr).all()


    
    
    
    
