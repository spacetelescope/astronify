import pytest

import numpy as np

from astropy.table import Table
from pyo import Server

from .. import SoniSeries, PitchMap
from ...utils.exceptions import InputWarning


def test_pitchmap():
    """
    Testing the PitchMap class.
    """
    
    # Defaults
    my_pitchmapper = PitchMap()
    assert isinstance(my_pitchmapper.pitch_map_args, dict)
    assert "center_pitch" in my_pitchmapper.pitch_map_args.keys()
    assert my_pitchmapper.pitch_map_args["zero_point"] == 'median'

    # Change args
    my_pitchmapper.pitch_map_args = {"pitch_range": [100, 10000],
                                     "center_pitch": 440,
                                     "zero_point": "mean",
                                     "stretch": "linear", 
                                     "invert": True}
    assert "center_pitch" in my_pitchmapper.pitch_map_args.keys()
    assert my_pitchmapper.pitch_map_args["zero_point"] == 'mean'

    with pytest.warns(InputWarning):  # setting with bad arg
        my_pitchmapper.pitch_map_args = {"pitch_range": [100, 10000],
                                         "center_pitch": 440,
                                         "zero_point": "mean",
                                         "stretch": "linear", 
                                         "penguin": True}
    
    assert "penguin" not in my_pitchmapper.pitch_map_args.keys()

    # Running function
    assert isinstance(my_pitchmapper([1, 1, 1, 1]), np.ndarray)

    # Changing function
    def my_map_func(data):  # dummy function
        data = np.array(data)
        return data/2

    with pytest.warns(InputWarning):  # because of different args     
        my_pitchmapper.pitch_map_func = my_map_func

    assert (my_pitchmapper([1, 1]) == [0.5, 0.5]).all()


def test_soniseries(tmpdir):
    """
    Testing SoniSeries class.
    """

    data = Table({"time": [0, 1, 2, 3, 4, 5, 6],
                  "flux": [1, 2, 1, 2, 5, 3, np.nan]})

    # defaults
    soni_obj = SoniSeries(data)
    assert soni_obj.note_duration == 0.5
    assert soni_obj.note_spacing == 0.01
    assert soni_obj.gain == 0.05
    assert isinstance(soni_obj.server, Server)
    assert len(soni_obj.data) == len(data) - 1  # nan row should be removed
    assert ~np.isnan(soni_obj.data["flux"]).any()
    assert soni_obj.data["flux"].dtype == np.float64

    soni_obj.sonify()
    assert "asf_pitch" in soni_obj.data.colnames
    assert "asf_onsets" in soni_obj.data.colnames
    assert soni_obj.data.meta['asf_exposure_time'] == 1
    assert soni_obj.data.meta['asf_note_duration'] == soni_obj.note_duration
    assert soni_obj.data.meta['asf_spacing'] == soni_obj.note_spacing
    
    onset_spacing = soni_obj.data['asf_onsets'][1:]-soni_obj.data['asf_onsets'][:-1]
    assert (np.isclose(onset_spacing, soni_obj.note_spacing)).all()

    pitch_min, pitch_max = soni_obj.pitch_mapper.pitch_map_args["pitch_range"]
    assert soni_obj.data["asf_pitch"].min() >= pitch_min
    assert soni_obj.data["asf_pitch"].max() <= pitch_max

    # TODO: change args and test

    # TODO: test write
