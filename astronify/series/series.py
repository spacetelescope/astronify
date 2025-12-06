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

__all__ = ["PitchMap", "SoniSeries"]


class PitchMap:

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
            pitch_args = {
                "pitch_range": [100, 10000],
                "center_pitch": 440,
                "zero_point": "median",
                "stretch": "linear",
            }

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
            param_types = [
                x.kind for x in signature(self.pitch_map_func).parameters.values()
            ]
            if Parameter.VAR_KEYWORD not in param_types:
                for arg_name in list(self.pitch_map_args):
                    if arg_name not in signature(self.pitch_map_func).parameters:
                        wstr = "{} is not accepted by the pitch mapping function and will be ignored".format(
                            arg_name
                        )
                        warnings.warn(wstr, InputWarning)
                        del self.pitch_map_args[arg_name]

    def __call__(self, data):
        """
        Apply the pitch mapping function to the data.
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
        assert isinstance(
            new_args, dict
        ), "Pitch mapping function args must be in a dictionary."
        self._pitch_map_args = new_args
        self._check_func_args()


class SoniSeries:
    # Default audio configuration parameters
    AUDIO_CONFIG = {
        # Envelope parameters for playback
        "play_envelope": [
            (0, 0),  # Start at silence
            (0.01, 1),  # Quick attack to full volume
            ("dur-0.1", 1),  # Hold at full volume until near end
            ("dur-0.05", 0.5),  # Start release
            ("dur-0.005", 0),  # End with silence
        ],
        # Envelope parameters for writing to file
        "write_envelope": [
            (0, 0),  # Start at silence
            (0.1, 1),  # Slower attack for files
            ("dur-0.1", 1),  # Hold at full volume until near end
            ("dur-0.05", 0.5),  # Start release
            ("dur-0.005", 0),  # End with silence
        ],
    }

    def __init__(self, data, time_col="time", val_col="flux", preview_type="scan"):
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
        preview_type : str
            Optional, default "scan". The mode of preview/gist sonification to
            make, choice of "ensemble" or "scan". Ensemble means each section
            is assigned a different pitch, played separately, then all sections
            are played together at the end. Scan means each section is assigned
            to the same pitch value, played separately, and no combined sound
            is made at the end.
        """
        self.time_col = time_col
        self.val_col = val_col
        self.data = data
        self.preview_type = preview_type

        # Default specs
        self.note_duration = 0.5  # note duration in seconds
        self.note_spacing = 0.01  # spacing between notes in seconds
        # default gain in the generated sine wave. pyo multiplier, -1 to 1.
        self.gain = 0.05
        self.pitch_mapper = PitchMap(data_to_pitch)
        self.preview_object = SeriesPreviews(self)
        self._init_pyo()

    def __enter__(self):
        """
        Context manager entry point - ensures server is ready.
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Context manager exit - clean up resources.
        """
        self.stop()
        if hasattr(self, 'server') and self.server is not None:
            if self.server.getIsBooted():
                self.server.shutdown()
        return False  # Don't suppress exceptions

    def _init_pyo(self):
        """Initialize the pyo audio server with safer defaults."""
        self.server = pyo.Server(
            sr=44100,  # Standard sample rate
            nchnls=1,  # Mono output (safer than stereo)
            buffersize=512,  # Smaller buffer size
            duplex=0,  # Don't try to use audio input
            audio='portaudio',  # Use the most compatible audio backend
            midi='none',  # Don't try to use MIDI
        )
        self.streams = None

    def _prepare_audio_data(self):
        """
        Common helper method to prepare audio data for playback or writing.
        Returns duration, pitches, and onsets data.
        """
        # Get values from metadata
        duration = self.data.meta["asf_note_duration"]

        # Prepare data for audio generation
        pitches = np.repeat(self.data["asf_pitch"], 2)
        onsets = np.repeat(self.data["asf_onsets"], 2)

        return duration, pitches, onsets

    def _create_envelope(self, duration, n_pitches, envelope_type="play_envelope"):
        """
        Create an envelope for audio based on the specified type.

        Parameters
        ----------
        duration : float
            The duration of each note in seconds
        n_pitches : int
            The number of pitches to create envelopes for
        envelope_type : str
            The type of envelope to use from AUDIO_CONFIG

        Returns
        -------
        pyo.Linseg
            The envelope object
        """
        # Get envelope points from config
        env_points = []
        for point in self.AUDIO_CONFIG[envelope_type]:
            # Process time points that are relative to duration
            if isinstance(point[0], str) and point[0].startswith("dur"):
                # Parse relative time points (e.g., "dur-0.1" becomes duration-0.1)
                time_expr = point[0].replace("dur", str(duration))
                time_val = eval(time_expr)
                env_points.append((time_val, point[1]))
            else:
                env_points.append(point)

        # Create the envelope
        return pyo.Linseg(list=env_points, mul=[self.gain for _ in range(n_pitches)])

    @property
    def data(self):
        """The data table (~astropy.table.Table)."""
        return self._data

    @data.setter
    def data(self, data_table):
        assert isinstance(data_table, Table), "Data must be a Table."

        if self.time_col not in data_table.columns:
            raise AttributeError(
                f"Input Table must contain time column '{self.time_col}'"
            )

        if self.val_col not in data_table.columns:
            raise AttributeError(
                f"Input Table must contain a value column '{self.val_col}'"
            )

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
        """The data column mapped to time when sonifying."""
        return self._time_col

    @time_col.setter
    def time_col(self, value):
        assert isinstance(value, str), "Time column name must be a string."
        self._time_col = value

    @property
    def val_col(self):
        """The data column mapped to pitch when sonifying."""
        return self._val_col

    @val_col.setter
    def val_col(self, value):
        assert isinstance(value, str), "Value column name must be a string."
        self._val_col = value

    @property
    def pitch_mapper(self):
        """The pitch mapping object that takes data values to pitch values (Hz)."""
        return self._pitch_mapper

    @pitch_mapper.setter
    def pitch_mapper(self, value):
        self._pitch_mapper = value

    @property
    def gain(self):
        """Adjustable gain for output."""
        return self._gain

    @gain.setter
    def gain(self, value):
        self._gain = value

    @property
    def note_duration(self):
        """How long each individual note will be in seconds."""
        return self._note_duration

    @note_duration.setter
    def note_duration(self, value):
        # Add in min value check
        self._note_duration = value

    @property
    def note_spacing(self):
        """The spacing of the notes on average (will adjust based on time) in seconds."""
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
        data["asf_onsets"] = [
            x
            for x in (data[self.time_col] - data[self.time_col][0])
            / exptime
            * self.note_spacing
        ]

    def play(self):
        """
        Play the data sonification.

        The sonification will play asynchronously. Use stop() to stop playback
        before completion.
        """
        try:
            # Safely handle server startup
            if self.server.getIsBooted():
                try:
                    self.stop()
                except:
                    self.server.shutdown()
                    self._init_pyo()

            # Boot and start server
            self.server.boot()
            self.server.start()

            # Prepare the audio data
            duration, pitches, onsets = self._prepare_audio_data()

            # Create envelope
            env = self._create_envelope(
                duration=duration, n_pitches=len(pitches), envelope_type="play_envelope"
            ).play(delay=list(onsets), dur=duration)

            # Create audio stream
            self.streams = pyo.Sine(list(pitches), 0, env).out(
                delay=list(onsets), dur=duration
            )

            return self

        except Exception as e:
            print(f"Audio playback error: {e}")
            return self

    def play_in_notebook(self):
        """
        Play the sonification in a Jupyter notebook using IPython.display.Audio
        This matches the original Pyo implementation but uses standard Python libraries.
        """
        try:
            from IPython.display import Audio, display
            import numpy as np

            # Sample rate
            sr = 44100

            # Get data from the same source as the original play method
            duration = self.data.meta["asf_note_duration"]

            # Repeat pitches and onsets exactly as in the original method
            pitches = np.repeat(self.data["asf_pitch"], 2)
            onsets = np.repeat(self.data["asf_onsets"], 2)

            # Calculate total audio length needed
            max_onset = max(onsets)
            total_duration = max_onset + duration + 0.5  # Add padding
            total_samples = int(sr * total_duration)

            # Create the audio buffer
            audio_buffer = np.zeros(total_samples)

            # Create an envelope function that matches the original Pyo Linseg envelope
            def create_envelope(duration_samples):
                # Convert time points to sample indices
                attack_end = int(0.01 * sr)
                sustain_end = int((duration - 0.1) * sr)
                fade_mid = int((duration - 0.05) * sr)
                fade_end = int((duration - 0.005) * sr)

                # Initialize envelope array
                env = np.zeros(duration_samples)

                # Attack phase: 0 to 0.01s (0 to 1)
                if attack_end > 0:
                    env[:attack_end] = np.linspace(0, 1, attack_end)

                # Sustain phase: 0.01s to (duration-0.1)s (value 1)
                if sustain_end > attack_end:
                    env[attack_end:sustain_end] = 1.0

                # First fade phase: (duration-0.1)s to (duration-0.05)s (1 to 0.5)
                if fade_mid > sustain_end:
                    env[sustain_end:fade_mid] = np.linspace(
                        1, 0.5, fade_mid - sustain_end
                    )

                # Final fade phase: (duration-0.05)s to (duration-0.005)s (0.5 to 0)
                if fade_end > fade_mid:
                    env[fade_mid:fade_end] = np.linspace(0.5, 0, fade_end - fade_mid)

                # Ensure zeros at the end
                if duration_samples > fade_end:
                    env[fade_end:] = 0

                return env

            # For each note
            for pitch, onset in zip(pitches, onsets):
                # Convert onset time to sample index
                onset_sample = int(onset * sr)

                # Duration in samples
                duration_samples = int(duration * sr)

                # Generate sine wave
                t = np.linspace(0, duration, duration_samples)
                sine_wave = np.sin(2 * np.pi * pitch * t)

                # Apply envelope and gain
                envelope = create_envelope(duration_samples)
                sine_wave = sine_wave * envelope * self.gain

                # Add to buffer (with bounds checking)
                end_sample = min(onset_sample + duration_samples, total_samples)
                if end_sample > onset_sample:
                    audio_length = end_sample - onset_sample
                    audio_buffer[onset_sample:end_sample] += sine_wave[:audio_length]

            # Normalize to prevent clipping
            max_val = np.max(np.abs(audio_buffer))
            if max_val > 0:
                audio_buffer = audio_buffer / max_val * 0.9

            # Display the audio widget
            display(Audio(audio_buffer, rate=sr))

        except Exception as e:
            print(f"Error generating audio: {e}")

    def stop(self):
        """
        Stop playing the data sonification.
        """
        if self.streams is not None:
            if isinstance(self.streams, list):
                for stream in self.streams:
                    if hasattr(stream, 'stop'):
                        stream.stop()
            elif hasattr(self.streams, 'stop'):
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
        try:
            # Prepare the audio data
            duration, pitches, onsets = self._prepare_audio_data()

            # Making sure we have a clean server
            if self.server.getIsBooted():
                self.server.shutdown()

            # Initialize offline server for rendering
            self.server.reinit(audio="offline")
            self.server.boot()

            # Configure recording options
            max_onset = max(onsets) if len(onsets) > 0 else 0
            self.server.recordOptions(dur=max_onset + duration, filename=filepath)

            # Create envelope with slightly different parameters for file output
            env = self._create_envelope(
                duration=duration,
                n_pitches=len(pitches),
                envelope_type="write_envelope",
            ).play(delay=list(onsets), dur=duration)

            # Create and play the sound
            sine = pyo.Sine(list(pitches), 0, env).out(delay=list(onsets), dur=duration)

            # Start rendering
            self.server.start()

            # Clean up
            self.server.shutdown()
            self.server.reinit(audio="portaudio")

        except Exception as e:
            print(f"Error writing audio file: {e}")

            # Try to clean up in case of error
            if hasattr(self, 'server') and self.server is not None:
                try:
                    self.server.shutdown()
                    self.server.reinit(audio="portaudio")
                except:
                    pass

    def play_in_notebook(self):
        """
        Alternative play method for notebooks that uses IPython.display.Audio
        instead of Pyo. This should be much more stable in notebook environments.
        """
        try:
            from IPython.display import Audio, display
            import numpy as np

            # Sample rate
            sr = 44100

            # Prepare the audio data
            duration, _, _ = self._prepare_audio_data()
            pitches = self.data["asf_pitch"].tolist()
            onsets = self.data["asf_onsets"].tolist()

            # Calculate the total duration
            max_onset = max(onsets) if onsets else 0
            total_duration = max_onset + duration + 0.5  # Add padding

            # Create the audio buffer
            audio_buffer = np.zeros(int(sr * total_duration))

            # Generate a simple envelope function
            def generate_envelope(duration_samples):
                attack = int(0.01 * sr)  # 10ms attack
                release = int(0.05 * sr)  # 50ms release
                sustain = duration_samples - attack - release

                env = np.zeros(duration_samples)
                # Attack
                env[:attack] = np.linspace(0, 1, attack)
                # Sustain
                env[attack : attack + sustain] = 1
                # Release
                env[attack + sustain :] = np.linspace(1, 0, release)
                return env

            # For each note in the data
            for pitch, onset in zip(pitches, onsets):
                # Convert onset to samples
                onset_sample = int(onset * sr)
                # Calculate note duration in samples
                duration_samples = int(duration * sr)

                # Generate sine wave
                t = np.linspace(0, duration, duration_samples)
                sine = np.sin(2 * np.pi * pitch * t)

                # Apply envelope
                sine = sine * generate_envelope(duration_samples) * self.gain

                # Add to buffer
                end_sample = min(onset_sample + duration_samples, len(audio_buffer))
                buffer_segment = audio_buffer[onset_sample:end_sample]
                sine_segment = sine[: len(buffer_segment)]
                audio_buffer[onset_sample:end_sample] += sine_segment

            # Normalize to prevent clipping
            max_val = np.max(np.abs(audio_buffer))
            if max_val > 0:
                audio_buffer = audio_buffer / max_val * 0.9

            # Display the audio widget
            display(Audio(audio_buffer, rate=sr))

        except Exception as e:
            print(f"Error generating audio: {e}")


class SeriesPreviews:
    """
    Previews (or snapshots) of 1d spectra by binning the data into five equal pieces by assigning a sound to each piece.
    """

    def __init__(self, soniseries):
        # Allows access to SoniSeries class methods and variables
        self._soniseries = soniseries
        # Define the frequencies to use for each section.
        self.pitch_values = [500] * 5
        if self._soniseries.preview_type == "ensemble":
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
            if idx < len(ydata_bins) - 1:
                # Then you need to include the first (x,y) point from the NEXT bin as well
                # when calculating the trapezoidal area so the pieces all add up to the total.
                list(ydata_bin).append(ydata_bins[idx + 1][0])
                list(xdata_bin).append(xdata_bins[idx + 1][0])

            # Taking the absolute value so that emission lines and absorption lines
            # have the same amplitude
            area_vals.append(np.abs(np.trapz(ydata_bin, xdata_bin)))
        return area_vals

    def plot_preview(self, xdata_bin_ranges):
        plt.plot(
            self._soniseries.data[self._soniseries.time_col],
            self._soniseries.data[self._soniseries.val_col],
            color="k",
        )

        plt.axvspan(
            xdata_bin_ranges[0][0],
            xdata_bin_ranges[0][1],
            color="royalblue",
            alpha=0.5,
            lw=0,
        )

        plt.axvspan(
            xdata_bin_ranges[1][0],
            xdata_bin_ranges[1][1],
            color="green",
            alpha=0.5,
            lw=0,
        )

        plt.axvspan(
            xdata_bin_ranges[2][0],
            xdata_bin_ranges[2][1],
            color="yellow",
            alpha=0.5,
            lw=0,
        )

        plt.axvspan(
            xdata_bin_ranges[3][0],
            xdata_bin_ranges[3][1],
            color="orange",
            alpha=0.5,
            lw=0,
        )

        plt.axvspan(
            xdata_bin_ranges[4][0],
            xdata_bin_ranges[4][1],
            color="red",
            alpha=0.5,
            lw=0,
        )

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
        ydata_norm = ydata / max(ydata)

        # Split the data into `n_pitch_values` equal-sized pieces.
        bin_size = int(np.round(len(xdata) // self.n_pitch_values, 1))
        # Split the y-values into pieces.
        ydata_bins = [
            ydata_norm[i : i + bin_size] for i in range(0, len(ydata_norm), bin_size)
        ]
        # Split the x-values into pieces.
        xdata_bins = [xdata[i : i + bin_size] for i in range(0, len(xdata), bin_size)]

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

        if std_dev_norm == 0.0:
            std_dev_norm = 1.0

        # Set the tremolo values based on the standard deviation of the piece normalized by the
        # `std_dev_norm` factor.

        # TODO: Might be worth trying a different way of calculating the tremolo values other
        # than the normalized standard dev. Maybe using RMS vals?
        # To more accurately represent all forms of data.

        # The final calculated tremolo values are multiplied by a factor of 10 for auditory
        # purposes
        self.tremolo_vals = (np.asarray(std_vals) / std_dev_norm) * 10

        # Constraint added to keep tremolo values at or below 15, otherwise oscillations are
        # more difficult to hear
        # self.tremolo_vals[self.tremolo_vals > 15] = 15

        if verbose:
            print("Total Expected area = {0:0f}".format(total_area))
            print(" ")
            print("Area Values = ", np.asarray(area_vals))
            print(" ")
            # print("Total Calculated area = {0:0f}".format(np.sum(str(area_vals).split(" "))))
            print(" ")
            print("Amplitudes = ", self.amplitudes)
            print(" ")
            print("Standard Dev. Error Vals = ", np.asarray(std_vals))
            print(" ")
            print("Standard Dev. Error MAX = ", std_dev_norm)
            print(" ")
            print("Tremolo Vals (x10) = ", self.tremolo_vals)

    def play_preview(self):
        """Play the sound of a "preview-style" sonification.

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
        self.delays = [0.0, 2.0, 4.0, 6.0, 8.0]

        # `total_duration` is in seconds
        self.total_duration = 8.0

        self.amplitudes = [amp / max(self.amplitudes) for amp in self.amplitudes]

        a = pyo.Phasor(self.pitch_values[0], mul=np.pi * 2)
        b = pyo.Phasor(self.pitch_values[1], mul=np.pi * 2)
        c = pyo.Phasor(self.pitch_values[2], mul=np.pi * 2)
        d = pyo.Phasor(self.pitch_values[3], mul=np.pi * 2)
        e = pyo.Phasor(self.pitch_values[4], mul=np.pi * 2)

        # TODO: Make everything below iterable to it's cleaner and takes up less lines
        lfo1 = (
            pyo.Sine(float(self.tremolo_vals[0]), 0, float(self.amplitudes[0]), 0)
            if self.tremolo_vals[0] > 0
            else pyo.Cos(a, mul=float(self.amplitudes[0]))
        )
        lfo2 = (
            pyo.Sine(float(self.tremolo_vals[1]), 0, float(self.amplitudes[1]), 0)
            if self.tremolo_vals[1] > 0
            else pyo.Cos(b, mul=float(self.amplitudes[1]))
        )
        lfo3 = (
            pyo.Sine(float(self.tremolo_vals[2]), 0, float(self.amplitudes[2]), 0)
            if self.tremolo_vals[2] > 0
            else pyo.Cos(c, mul=float(self.amplitudes[2]))
        )
        lfo4 = (
            pyo.Sine(float(self.tremolo_vals[3]), 0, float(self.amplitudes[3]), 0)
            if self.tremolo_vals[3] > 0
            else pyo.Cos(d, mul=float(self.amplitudes[3]))
        )
        lfo5 = (
            pyo.Sine(float(self.tremolo_vals[4]), 0, float(self.amplitudes[4]), 0)
            if self.tremolo_vals[4] > 0
            else pyo.Cos(e, mul=float(self.amplitudes[4]))
        )

        # Create streams using list comprehension
        stream_info = [
            (self.pitch_values[i], self.delays[i], 2.0, lfo)
            for i, lfo in enumerate([lfo1, lfo2, lfo3, lfo4, lfo5])
        ]

        self.streams = []
        for pitch, delay, dur, lfo in stream_info:
            stream = pyo.Sine(freq=[pitch, pitch], mul=lfo).out(delay=delay, dur=dur)
            self.streams.append(stream)

        # All together, if in ensemble mode.
        if self._soniseries.preview_type == "ensemble":
            ensemble_streams = []
            for pitch, _, _, lfo in stream_info:
                stream = pyo.Sine(freq=[pitch, pitch], mul=lfo).out(delay=10, dur=4)
                ensemble_streams.append(stream)

            # Add ensemble streams to the main streams list
            self.streams.extend(ensemble_streams)
