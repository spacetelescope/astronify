# Licensed under a 3-clause BSD style license - see LICENSE.rst
"""
Data Series Sonification
========================

Functionality for sonifying data series.
"""

import warnings

from inspect import signature, Parameter

import numpy as np
from scipy import stats
from astropy.table import Table, MaskedColumn
from astropy.time import Time

import matplotlib.pyplot as plt 

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
        self.preview_object = SeriesPreviews(self)

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


class SeriesPreviews():
        """ Previews (or snapshots) of 1d spectra by binning the data into
        five equal pieces by assigning a sound to each piece. 
        """

        def __init__(self, soniseries):
            # Allows access to SoniSeries class methods and variables
            self._soniseries = soniseries
            # Define the frequencies to use for each piece.
            self.pitch_values = [300, 400, 500, 600, 700]
            # TODO: Make robust
            self.n_pitch_values = len(self.pitch_values)
            # Amplitudes will be stored as a % between 0-1.
            self.amplitudes = np.zeros(self.n_pitch_values)
            # Tremolo values will be stored as a number, typically ranging from some small number
            # (avoid 0.0, e.g., 0.1) through ~10.
            self.tremolo_vals = np.zeros(self.n_pitch_values)

        def area_of_pieces(self, ydata_bins, xdata_bins):
            """
            Given pieces of a series of 1D data, calculate the area-under-the-curve of each piece
            such that the total area of all the pieces equals the total area of the entire curve.
            """
            area_vals = []
            for idx, (ydata_bin, xdata_bin) in enumerate(zip(ydata_bins, xdata_bins)):
                if idx < len(ydata_bins)-1:
                    # Then you need to include the first (x,y) point from the NEXT bin as well
                    # when calculating the trapezoidal area so the pieces all add up to the total.
                    list(ydata_bin).append(ydata_bins[idx+1][0])
                    list(xdata_bin).append(xdata_bins[idx+1][0])

                # Taking the absolute value so that emission lines and absorption lines 
                # have the same amplitude
                area_vals.append(np.abs(np.trapz(ydata_bin, xdata_bin)))
            return area_vals

        def plot_preview(self, xdata_bin_ranges): 

            plt.plot(self._soniseries.data[self._soniseries.time_col], self._soniseries.data[self._soniseries.val_col], color='k')

            plt.axvspan(xdata_bin_ranges[0][0], xdata_bin_ranges[0][1], color='r', alpha=0.5, lw=0)
            plt.axvspan(xdata_bin_ranges[1][0], xdata_bin_ranges[1][1], color='orange', alpha=0.5, lw=0)
            plt.axvspan(xdata_bin_ranges[2][0], xdata_bin_ranges[2][1], color='y', alpha=0.5, lw=0)
            plt.axvspan(xdata_bin_ranges[3][0], xdata_bin_ranges[3][1], color='g', alpha=0.5, lw=0)
            plt.axvspan(xdata_bin_ranges[4][0], xdata_bin_ranges[4][1], color='royalblue', alpha=0.5, lw=0)

            plt.show()

        def sonify_preview(self, plotting=True, verbose=False):
            """
            Make a "preview-style" sonification.  The data is split into even pieces.  Each piece
            gets assigned a specific frequency.  The amplitude is defined by the area under the curve
            in this piece, normalized by the total area under the curve.  The tremolo is defined
            by the standard deviation of data in this piece, normalized by the maximum standard
            deviation across all pieces.
            """
            # Get a copy of the 'y' and 'x' data.
            ydata = np.asarray(self._soniseries.data[self._soniseries.val_col])
            xdata = np.asarray(self._soniseries.data[self._soniseries.time_col])

            # Normalize the y-data by the maximum to constrain values from 0-1.
            ydata_norm = ydata/max(ydata)

            # Split the data into `n_pitch_values` equal-sized pieces.
            bin_size = int(np.round(len(xdata) // self.n_pitch_values, 1))
            # Split the y-values into pieces.
            ydata_bins = [ydata_norm[i:i+bin_size] for i in range(0, len(ydata_norm), bin_size)]
            # Split the x-values into pieces.
            xdata_bins = [xdata[i:i+bin_size] for i in range(0, len(xdata), bin_size)]
            
            # Calculate the total area under the curve, used to normalize the areas in each piece.
            total_area = np.trapz(ydata_norm, xdata)

            # Loop through each piece and calculate the standard deviation of the y-data
            # and the area under the curve in each piece.
            std_vals, xdata_bin_ranges = [], []
            for xdata_bin, ydata_bin in zip(xdata_bins, ydata_bins):

                xdata_bin_ranges.append((min(xdata_bin), max(xdata_bin)))
                # Calculate standard deviation error and add to the list.
                _, _, _, _, std_err = stats.linregress(xdata_bin, ydata_bin)
                std_vals.append(std_err)
                #std_vals.append(np.std(ydata_bin))
                
            # Plot the spectra and ranges if in troubleshooting mode
            if plotting:
                self.plot_preview(xdata_bin_ranges)

            # Calculate the area under the curve for each piece.
            area_vals = self.area_of_pieces(ydata_bins, xdata_bins)

            # Normalize the standard deviations in each piece by this factor.
            std_dev_norm = max(std_vals)

            # Set the amplitude of each pitch to the area under the curve normalized by the total
            # area.
            self.amplitudes = np.asarray(area_vals) / total_area
            
            if std_dev_norm == 0.0: std_dev_norm = 1.0

            # Set the tremolo values based on the standard deviation of the piece normalized by the
            # `std_dev_norm` factor.

            # TODO: Might be worth trying a different way of calculating the tremolo values other 
            # than the normalized standard dev. Maybe using RMS vals? 
            # To more accurately represent all forms of data.

            # The final calculated tremolo values are multiplied by a factor of 10 for auditory 
            # purposes
            self.tremolo_vals = (np.asarray(std_vals) / std_dev_norm)*10

            # Constraint added to keep tremolo values at or below 15, otherwise oscillations are 
            # more difficult to hear 
            #self.tremolo_vals[self.tremolo_vals > 15] = 15

            if verbose:
                print('Total Expected area = {0:0f}'.format(total_area))
                print(' ')
                print('Area Values = ', np.asarray(area_vals))
                print(' ')
                #print('Total Calculated area = {0:0f}'.format(np.sum(str(area_vals).split(' '))))
                print(' ')
                print('Amplitudes = ', self.amplitudes)
                print(' ')
                print('Standard Dev. Error Vals = ', np.asarray(std_vals))
                print(' ')
                print('Standard Dev. Error MAX = ', std_dev_norm)
                print(' ')
                print('Tremolo Vals (x10) = ', self.tremolo_vals)


        def play_preview(self):
            """ Play the sound of a "preview-style" sonification.

            The assigned pitch for each section of the spectra will begin
            to play, with the calculated amplitude and frequency, one 
            at a time until all pitches are playing together for the full 
            audio preview of the spectra.
            """
            
            if self._soniseries.server.getIsBooted():
                self._soniseries.server.shutdown()
        
            self._soniseries.server.boot()
            self._soniseries.server.start()
            
            # TODO: Generalize the self.delays list
            # `step` must go into `stop` 5 times, since we have 5 pitches
            #start, stop, step = 0, 2.5, 0.5 
            #self.delays = np.arange(start, stop, step)
            self.delays = [0., 2., 4., 6., 8.]

            # `total_duration` is in seconds
            self.total_duration = 8.0 
            
            default = 1.0 #float(min(self.amplitudes))#float((max(self.amplitudes) - min(self.amplitudes))/2)
            self.amplitudes = [amp/max(self.amplitudes) for amp in self.amplitudes]

            a = pyo.Phasor(self.pitch_values[0], mul=np.pi*2)
            b = pyo.Phasor(self.pitch_values[1], mul=np.pi*2)
            c = pyo.Phasor(self.pitch_values[2], mul=np.pi*2)
            d = pyo.Phasor(self.pitch_values[3], mul=np.pi*2)
            e = pyo.Phasor(self.pitch_values[4], mul=np.pi*2)
            

            # TODO: Make everything below iterable to it's cleaner and takes up less lines
            lfo1 = pyo.Sine(float(self.tremolo_vals[0]), 0, float(self.amplitudes[0]), 0) if self.tremolo_vals[0] > 0 else pyo.Cos(a, mul=float(self.amplitudes[0]))
            lfo2 = pyo.Sine(float(self.tremolo_vals[1]), 0, float(self.amplitudes[1]), 0) if self.tremolo_vals[1] > 0 else pyo.Cos(b, mul=float(self.amplitudes[1]))
            lfo3 = pyo.Sine(float(self.tremolo_vals[2]), 0, float(self.amplitudes[2]), 0) if self.tremolo_vals[2] > 0 else pyo.Cos(c, mul=float(self.amplitudes[2]))
            lfo4 = pyo.Sine(float(self.tremolo_vals[3]), 0, float(self.amplitudes[3]), 0) if self.tremolo_vals[3] > 0 else pyo.Cos(d, mul=float(self.amplitudes[3]))
            lfo5 = pyo.Sine(float(self.tremolo_vals[4]), 0, float(self.amplitudes[4]), 0) if self.tremolo_vals[4] > 0 else pyo.Cos(e, mul=float(self.amplitudes[4]))

            self.stream1 = pyo.Sine(freq=self.pitch_values[0], mul=lfo1).out(delay=self.delays[0], dur=2.0)
            
            self.stream2 = pyo.Sine(freq=self.pitch_values[1], mul=lfo2).out(delay=self.delays[1], dur=2.0)

            self.stream3 = pyo.Sine(freq=self.pitch_values[2], mul=lfo3).out(delay=self.delays[2], dur=2.0)

            self.stream4 = pyo.Sine(freq=self.pitch_values[3], mul=lfo4).out(delay=self.delays[3], dur=2.0)

            self.stream5 = pyo.Sine(freq=self.pitch_values[4], mul=lfo5).out(delay=self.delays[4], dur=2.0)

            # All together
            self.stream6 = pyo.Sine(freq=self.pitch_values[0], mul=lfo1).out(delay=10, dur=4)
            
            self.stream7 = pyo.Sine(freq=self.pitch_values[1], mul=lfo2).out(delay=10, dur=4)

            self.stream8 = pyo.Sine(freq=self.pitch_values[2], mul=lfo3).out(delay=10, dur=4)

            self.stream9 = pyo.Sine(freq=self.pitch_values[3], mul=lfo4).out(delay=10, dur=4)

            self.stream10 = pyo.Sine(freq=self.pitch_values[4], mul=lfo5).out(delay=10, dur=4)
            
