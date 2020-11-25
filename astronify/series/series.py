# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Data Series Sonification
========================

Functionality for sonifying data series.
"""

import warnings

from inspect import signature, Parameter

import numpy as np

from astropy.table import Table, MaskedColumn
from astropy.time import Time

import pyo

from ..utils.pitch_mapping import data_to_pitch
from ..utils.exceptions import InputWarning

__all__ = ['PitchMap', 'SoniSeries']


class PitchMap():

    def __init__(self, pitch_func=data_to_pitch, **pitch_args):
        """
        Class that encapsulates the data value to pitch function 
        and associated arguments.

        Parameters
        ----------
        pitch_func : function
            Optional. Defaults to `~astronify.utils.data_to_pitch`.
            If supplying a function it should take a data array as the first
            parameter, and all other parameters should be optional.
        **pitch_args 
            Default parameters and values for the pitch function. Should include
            all necessary arguments other than the data values.
        """

        # Setting up the default arguments
        if (not pitch_args) and (pitch_func == data_to_pitch):
            pitch_args = {"pitch_range": [100, 10000],
                          "center_pitch": 440,
                          "zero_point": "median",
                          "stretch": "linear"}
        
        self.pitch_map_func = pitch_func
        self.pitch_map_args = pitch_args

        
    def _check_func_args(self):
        """
        Make sure the pitch mapping function and argument dictionary match.

        Note: This function does not check the the function gets all the required arguments.
        """
        # Only test if both pitch func and args are set
        if hasattr(self, "pitch_map_func") and hasattr(self, "pitch_map_args"):

            # Only check parameters if there is no kwargs argument
            param_types = [x.kind for x in signature(self.pitch_map_func).parameters.values()]
            if Parameter.VAR_KEYWORD not in param_types:
                for arg_name in list(self.pitch_map_args):
                    if arg_name not in signature(self.pitch_map_func).parameters:
                        wstr = "{} is not accepted by the pitch mapping function and will be ignored".format(arg_name)
                        warnings.warn(wstr, InputWarning)
                        del self.pitch_map_args[arg_name]

    def __call__(self, data):
        """
        Where does this show up?
        """
        self._check_func_args()
        return self.pitch_map_func(data, **self.pitch_map_args)

    @property
    def pitch_map_func(self):
        """
        The pitch mapping function. 
        """
        return self._pitch_map_func

    @pitch_map_func.setter
    def pitch_map_func(self, new_func):
        assert callable(new_func), "Pitch mapping function must be a function."
        self._pitch_map_func = new_func
        self._check_func_args()

    @property
    def pitch_map_args(self):
        """
        Dictionary of additional arguments (other than the data array)
        for the pitch mapping function.
        """
        return self._pitch_map_args

    @pitch_map_args.setter
    def pitch_map_args(self, new_args):
        assert isinstance(new_args, dict), "Pitch mapping function args must be in a dictionary."
        self._pitch_map_args = new_args
        self._check_func_args()

             

class SoniSeries():

    def __init__(self, data, time_col="time", val_col="flux"):
        """
        Class that encapsulates a sonified data series.

        Parameters
        ----------
        data : `astropy.table.Table`
            The table of data to be sonified.
        time_col : str
            Optional, default "time". The data column to be mapped to time.
        val_col : str
            Optional, default "flux". The data column to be mapped to pitch.
        """
        self.time_col = time_col
        self.val_col = val_col
        self.data = data

        # Default specs
        self.note_duration = 0.5  # note duration in seconds
        self.note_spacing = 0.01  # spacing between notes in seconds
        self.gain = 0.05  # default gain in the generated sine wave. pyo multiplier, -1 to 1.
        self.pitch_mapper = PitchMap(data_to_pitch)

        self._init_pyo()

    def _init_pyo(self):
        self.server = pyo.Server()
        self.streams = None

    @property
    def data(self):
        """ The data table (~astropy.table.Table). """
        return self._data

    @data.setter
    def data(self, data_table):
        assert isinstance(data_table, Table), 'Data must be a Table.'

        # Removing any masked values as they interfere with the sonification
        if isinstance(data_table[self.val_col], MaskedColumn):
            data_table = data_table[~data_table[self.val_col].mask]
        if isinstance(data_table[self.time_col], MaskedColumn):
            data_table = data_table[~data_table[self.time_col].mask]

        # Removing any nans as they interfere with the sonification
        data_table = data_table[~np.isnan(data_table[self.val_col])]

        # making sure we have a float column for time
        if isinstance(data_table[self.time_col], Time):
            float_col = "asf_time"
            data_table[float_col] = data_table[self.time_col].jd
            self.time_col = float_col
            
        self._data = data_table

    @property
    def time_col(self):
        """ The data column mappend to time when sonifying. """
        return self._time_col

    @time_col.setter
    def time_col(self, value):
        assert isinstance(value, str), 'Time column name must be a string.'
        self._time_col = value

    @property
    def val_col(self):
        """ The data column mappend to putch when sonifying. """
        return self._val_col

    @val_col.setter
    def val_col(self, value):
        assert isinstance(value, str), 'Value column name must be a string.'
        self._val_col = value

    @property
    def pitch_mapper(self):
        """ The pitch mapping object that takes data values to pitch values (Hz). """
        return self._pitch_mapper

    @pitch_mapper.setter
    def pitch_mapper(self, value):
        self._pitch_mapper = value

    @property
    def gain(self):
        """ Adjustable gain for output. """
        return self._gain

    @gain.setter
    def gain(self, value):
        self._gain = value

    @property
    def note_duration(self):
        """ How long each individual note will be in seconds."""
        return self._note_duration

    @note_duration.setter
    def note_duration(self, value):
        # Add in min value check
        self._note_duration = value

    @property
    def note_spacing(self):
        """ The spacing of the notes on average (will adjust based on time) in seconds. """
        return self._note_spacing

    @note_spacing.setter
    def note_spacing(self, value):
        # Add in min value check
        self._note_spacing = value
        
    def sonify(self):
        """
        Perform the sonification, two columns will be added to the data table: asf_pitch, and asf_onsets. 
        The asf_pitch column will contain the sonified data in Hz.
        The asf_onsets column will contain the start time for each note in seconds from the first note.
        Metadata will also be added to the table giving information about the duration and spacing 
        of the sonified pitches, as well as an adjustable gain.
        """
        data = self.data
        exptime = np.median(np.diff(data[self.time_col]))

        data.meta["asf_exposure_time"] = exptime
        data.meta["asf_note_duration"] = self.note_duration
        data.meta["asf_spacing"] = self.note_spacing
        
        data["asf_pitch"] = self.pitch_mapper(data[self.val_col])
        data["asf_onsets"] = [x for x in (data[self.time_col] - data[self.time_col][0])/exptime*self.note_spacing]

    def play(self):
        """
        Play the data sonification.
        """

        # Making sure we have a clean server
        if self.server.getIsBooted():
            self.server.shutdown()

        self.server.boot()
        self.server.start()

        # Getting data ready
        duration = self.data.meta["asf_note_duration"]
        pitches = np.repeat(self.data["asf_pitch"], 2)
        delays = np.repeat(self.data["asf_onsets"], 2)

        # TODO: This doesn't seem like the best way to do this, but I don't know
        # how to make it better
        env = pyo.Linseg(list=[(0, 0), (0.01, 1), (duration - 0.1, 1),
                               (duration - 0.05, 0.5), (duration - 0.005, 0)],
                         mul=[self.gain for i in range(len(pitches))]).play(
                             delay=list(delays), dur=duration)

        self.streams = pyo.Sine(list(pitches), 0, env).out(delay=list(delays),
                                                           dur=duration)

    def stop(self):
        """
        Stop playing the data sonification.
        """
        self.streams.stop() 

    def write(self, filepath):
        """
        Save data sonification to the given file. 
        Currently the only output option is a wav file.

        Parameters
        ----------
        filepath : str
            The path to the output file.
        """

        # Getting data ready
        duration = self.data.meta["asf_note_duration"]
        pitches = np.repeat(self.data["asf_pitch"], 2)
        delays = np.repeat(self.data["asf_onsets"], 2)

        # Making sure we have a clean server
        if self.server.getIsBooted():
            self.server.shutdown()

        self.server.reinit(audio="offline")
        self.server.boot()
        self.server.recordOptions(dur=delays[-1]+duration, filename=filepath)

        env = pyo.Linseg(list=[(0, 0), (0.1, 1), (duration - 0.1, 1),
                               (duration - 0.05, 0.5), (duration - 0.005, 0)],
                         mul=[self.gain for i in range(len(pitches))]).play(
                             delay=list(delays), dur=duration)
        sine = pyo.Sine(list(pitches), 0, env).out(delay=list(delays), dur=duration)  # noqa: F841
        self.server.start()

        # Clean up
        self.server.shutdown()
        self.server.reinit(audio="portaudio")

