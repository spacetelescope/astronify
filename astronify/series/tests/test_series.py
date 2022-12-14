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


class TestSoniSeries(object):

    @classmethod
    def setup_class(cls):

        cls.data = Table({"time": [0, 1, 2, 3, 4, 5, 6],
                          "Flux": [1, 2, 1, 2, 5, 3, np.nan]})

        cls.soni_obj = SoniSeries(cls.data)

    def test_soniseries_initializes(self):
        SoniSeries(self.data)

    def test_conversion_to_lowercase(self):
        assert list(self.soni_obj.data.columns)[1] == "flux"

    def test_assert_time_exists(self):

        new_data = Table({"foo": [0, 1, 2, 3, 4, 5, 6],
                          "Flux": [1, 2, 1, 2, 5, 3, np.nan]})
    
        with pytest.raises(AssertionError):
            so = SoniSeries(new_data)    

    def test_assert_flux_exists(self):
        
        new_data = Table({"time": [0, 1, 2, 3, 4, 5, 6],
                          "bar": [1, 2, 1, 2, 5, 3, np.nan]})
        
        with pytest.raises(AssertionError):
            so = SoniSeries(new_data)

    def test_default_parameters(self):
        assert self.soni_obj.note_duration == 0.5
        assert self.soni_obj.note_spacing == 0.01
        assert self.soni_obj.gain == 0.05

    def test_server_class(self):
        assert isinstance(self.soni_obj.server, Server)

    def test_nans_removed(self):
        assert len(self.soni_obj.data) == len(self.data) - 1  # nan row should be removed
        assert ~np.isnan(self.soni_obj.data["flux"]).any()

    def test_flux_type_correct(self):
        assert self.soni_obj.data["flux"].dtype == np.float64

    def test_sonify_works(self):
        self.soni_obj.sonify()

    def test_sonify_new_columns_exist(self):
        assert "asf_pitch" in self.soni_obj.data.colnames
        assert "asf_onsets" in self.soni_obj.data.colnames

    def test_sonify_metadata(self):
        assert self.soni_obj.data.meta['asf_exposure_time'] == 1
        assert self.soni_obj.data.meta['asf_note_duration'] == self.soni_obj.note_duration
        assert self.soni_obj.data.meta['asf_spacing'] == self.soni_obj.note_spacing

    def test_onset_spacing(self):
        onset_spacing = self.soni_obj.data['asf_onsets'][1:]-self.soni_obj.data['asf_onsets'][:-1]
        assert (np.isclose(onset_spacing, self.soni_obj.note_spacing)).all()

    def test_pitch_min_max(self):
        pitch_min, pitch_max = self.soni_obj.pitch_mapper.pitch_map_args["pitch_range"]
        assert self.soni_obj.data["asf_pitch"].min() >= pitch_min
        assert self.soni_obj.data["asf_pitch"].max() <= pitch_max

    # TODO: change args and test

    # TODO: test write


