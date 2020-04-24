# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Data Series Sonification
========================

Functionality for sonifying data series.
"""

import os

import numpy as np

from astropy.table import Table
from astropy.io import fits

import pyo
import thinkdsp

from .utils.pitch_mapping import data_to_pitch


class SoniSeries():
    """

    Clase that encapsulated a sonified data series.

    TODO: finish documentation
    """

    def __init__(self, data, method="pyo", time_col="time", val_col="flux"):
        self.data = data
        self.sonification_method = method
        self.time_col = time_col
        self.val_col = val_col

        self.pitch_map = data_to_pitch

        if method == "pyo":
            self._init_pyo()

    def _init_pyo(self):
        self.server = pyo.Server()
        self.streams = None

    @property
    def sonification_method(self):
        return self._sonification_method

    @sonification_method.setter
    def sonification_method(self, value):
        method_warn_str = ('The only valid sonification methods are pyo and'
                           ' thinkdsp.')
        assert value.lower() in ("pyo", "thinkdsp"), method_warn_str
        self._sonification_method = value
        if value == "pyo":
            self._init_pyo()

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        assert isinstance(value, Table), 'Data must be a Table.'
        self._data = value

    @property
    def time_col(self):
        return self._time_col

    @time_col.setter
    def time_col(self, value):
        assert isinstance(value, str), 'Time column name must be a string.'
        self._time_col = value

    @property
    def val_col(self):
        return self._val_col

    @val_col.setter
    def val_col(self, value):
        assert isinstance(value, str), 'Value column name must be a string.'
        self._val_col = value

    @property
    def pitch_map(self):
        return self._pitch_map

    @pitch_map.setter
    def pitch_map(self, value):
        # TODO: test for valid function here
        self._pitch_map = value

    def sonify(self):
        """
        TODO: document, also add arguments
        """
        duration = 0.5 # note duration in seconds
        spacing = 0.01 # spacing between notes in seconds
        data = self.data

        # NOTE: This assumes the times in the time_col are an astropy Time object
        # and thus the np.diff results in a TimeDelta object with structured tags
        # If passing, e.g., simulated data from the simulator, it may not be?
        exptime = np.median(np.diff(data[self.time_col])).value

        data.meta["exposure_time"] = exptime
        data.meta["note_duration"] = duration
        data.meta["spacing"] = spacing

        data["pitch"] = self.pitch_map(data[self.val_col])
        data["onsets"] = [x for x in (data["time"].jd -
                                      data["time"].jd[0])/exptime*spacing]

    def _pyo_play(self):
        """
        TODO: document
        """

        # Making sure we have a clean server
        if self.server.getIsBooted():
            self.server.shutdown()

        self.server.boot()
        self.server.start()

        # Getting data ready
        duration = self.data.meta["note_duration"]
        pitches = np.repeat(self.data["pitch"], 2)
        delays = np.repeat(self.data["onsets"], 2)

        # TODO: This doesn't seem like the best way to do this, but I don't know
        # how to make it better
        env = pyo.Linseg(list=[(0, 0), (0.01, 1), (duration - 0.1, 1),
                               (duration - 0.05, 0.5), (duration - 0.005, 0)],
                         mul=[.1 for i in range(len(pitches))]).play(
                             delay=list(delays), dur=duration)

        self.streams = pyo.Sine(list(pitches), 0, env).out(delay=list(delays),
                                                           dur=duration)

    def _pyo_stop(self):
        """
        TODO: document
        """

        self.streams.stop() # I think this is all?

    def _pyo_write(self, filepath):
        """
        TODO: document
        """

        # Getting data ready
        duration = self.data.meta["note_duration"]
        pitches = np.repeat(self.data["pitch"], 2)
        delays = np.repeat(self.data["onsets"], 2)

        # Making sure we have a clean server
        if self.server.getIsBooted():
            self.server.shutdown()

        self.server.reinit(audio="offline")
        self.server.boot()
        self.server.recordOptions(dur=delays[-1]+duration, filename=filepath)

        env = pyo.Linseg(list=[(0, 0), (0.1, 1), (duration - 0.1, 1),
                               (duration - 0.05, 0.5), (duration - 0.005, 0)],
                         mul=[0.05 for i in range(len(pitches))]).play(
                             delay=list(delays), dur=duration)
        sine = pyo.Sine(list(pitches), 0, env).out(delay=list(delays),
                                                   dur=duration)
        self.server.start()

        # Clean up
        self.server.shutdown()
        self.server.reinit(audio="portaudio")

    def _thinkdsp_play(self):
        pass

    def _thinkdsp_stop(self):
        pass

    def _thinkdsp_write(self, filepath):
        pass

    def play(self):
        """
        TODO: document
        """
        if self.sonification_method == "pyo":
            self._pyo_play()
        else:  # thinkdsp
            self._thinkdsp_play()

    def stop(self):
        """
        TODO: document
        """
        if self.sonification_method == "pyo":
            self._pyo_stop()
        else:  # thinkdsp
            self._thinkdsp_stop()

    def write(self, filepath):
        """
        TODO: document
        """
        if self.sonification_method == "pyo":
            self._pyo_write(filepath)
        else:  # thinkdsp
            self._thinkdsp_write(filepath)
