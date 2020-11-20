"""
.. module:: sim_lc
   :synopsis: Creates simulated light curves with a variety of signals in them
       in a FITS format. The files are designed to be read by the Astronify
       software package to use when testing the sonification process.

.. moduleauthor:: Scott W. Fleming <fleming@stsci.edu>
"""

from astropy.io import fits
from astropy.table import Table
import matplotlib.pyplot as plt
import numpy as np
import os
from .sim_lc_config import SimLcConfig
from .add_flare_signal import add_flare_signal
from .add_lc_noise import add_lc_noise
from .add_sine_signal import add_sine_signal
from .add_transit_signal import add_transit_signal
from .check_transit_params import check_transit_params
from .check_flare_params import check_flare_params
from .sim_lc_setup_args import sim_lc_setup_args


__all__ = ["simulated_lc", 'SimLcConfig']


def simulated_lc(lc_type, lc_ofile=SimLcConfig.sim_lc_ofile,
                 lc_length=SimLcConfig.sim_lc_length,
                 lc_noise=SimLcConfig.sim_lc_noise,
                 visualize=SimLcConfig.sim_lc_visualize,
                 lc_yoffset=SimLcConfig.sim_lc_yoffset,
                 transit_depth=SimLcConfig.sim_lc_transit_depth,
                 transit_period=SimLcConfig.sim_lc_transit_period,
                 transit_start=SimLcConfig.sim_lc_transit_start,
                 transit_width=SimLcConfig.sim_lc_transit_width,
                 sine_amp=SimLcConfig.sim_lc_sine_amp,
                 sine_period=SimLcConfig.sim_lc_sine_period,
                 flare_time=SimLcConfig.sim_lc_flare_time,
                 flare_amp=SimLcConfig.sim_lc_flare_amp,
                 flare_halfwidth=SimLcConfig.sim_lc_flare_halfwidth):
    """
    Create light curve with specified parameters as a `~astropy.table.Table`,
    and optionally writes a FITS file with the same information.

    All parameters default to the configuration values.

    Parameters
    ----------
    lc_type : str
        The type of light curve to make. Valid options are 'flat', 'transit',
        'sine', and 'flare'.

    lc_ofile : str or None
        Optional. Name of output FITS file.  If set to None,
        no file will be saved to disk.

    lc_length : int
        Optional. Length of the light curve (i.e. the number of flux values).

    lc_noise : float
        Optional. Standard deviation of normal distribution to draw from when
        adding noise, a value of zero means no noise is added.

    visualize : bool
        Optional. If True, plot the light curve being made to the screen.

    lc_yoffset : float
        Optional. Baseline flux level (unitless).

    transit_depth: float
        Depth of transit, as a percent (e.g., 10.0 = 10%.)

    transit_period : int
        Period of transit (number of fluxes/bins between the start of each event.)
        (Only relevant for transit type light curve).

    transit_start : int
        Start index of transit (the index of the flux/bin to use as the start of the first transit
        event.)
        (Only relevant for transit type light curve).

    transit_width : int
        Width of transit (number of fluxes/bins between the start and end of each event.)

    sine_amp : float
        Amplitude of the sinusoidal signal to add.

    sine_period : float
        Period of the sinusoidal signal to add.

    flare_time: int
        Time corresponding to the maximum flare flux.

    flare_amp : float
        The peak (maximum flux) of the flare.

    flare_halfwidth : float
        The flare half-width (measured in indices) that
        corresponds to "t_1/2" in the Davenport et al. flare template.

    Returns
    --------
    response : `~astropy.table.Table`
        The time and flux columns.
    """

    # Generate baseline light curve fluxes.
    fluxes = np.full(lc_length, lc_yoffset)

    # We don't need real times for the simulation, it's just an array of indexes.
    times = np.arange(fluxes.size)

    # Apply signal of choice if needed.
    if lc_type == "flare":
        check_flare_params(fluxes.size, flare_time, flare_amp)
        fluxes = add_flare_signal(fluxes, flare_time, flare_amp, flare_halfwidth)
    elif lc_type == "sine":
        fluxes = add_sine_signal(times, fluxes, sine_amp, sine_period)
    elif lc_type == 'transit':
        check_transit_params(fluxes.size, transit_period, transit_start,
                             transit_width)
        fluxes = add_transit_signal(fluxes, transit_depth, transit_period,
                                    transit_start, transit_width)

    # Add noise based on standard deviation.
    fluxes_with_noise = add_lc_noise(fluxes, lc_noise)

    # Visualize the light curve, if desired.
    if visualize:
        _, ax1 = plt.subplots(1)
        ax1.plot(times, fluxes_with_noise, 'bo')
        plt.show()

    if lc_ofile:
        # Save light curve as FITS file.
        hdr = fits.Header()
        # Add input arguments as keyword headers here.
        hdr.append(("LCTYPE", lc_type, "Type of signal."))
        hdr.append(("LCLENGTH", lc_length, "Number of fluxes."))
        hdr.append(("LCYOFF", lc_yoffset, "Baseline flux value (unitless)."))
        hdr.append(("LCNOISE", lc_noise, "Std. dev. of normal dist. used to"
                    " apply noise."))
        # Record the flare parameters used if adding a flare.
        if lc_type == "flare":
            hdr.append(("FLARETIM", flare_time, "Index corresponding to the peak"
                        " of the flare."))
            hdr.append(("FLAREAMP", flare_amp, "Amplitude of the flare."))
            hdr.append(("FLAREWID", flare_halfwidth, "Flare half-width"
                        " (number of indices)."))
        # Record the sinusoidal parameters if adding a sinusoid.
        if lc_type == "sine":
            hdr.append(("SINEAMP", sine_amp, "Amplitude of sine."))
            hdr.append(("SINEPER", sine_amp, "Period of sine."))
        # Record the transit parameters if adding a transit.
        if lc_type == "transit":
            hdr.append(("TRANDEP", transit_depth, "Depth of transit."))
            hdr.append(("TRANPER", transit_period, "Period of planet."))
            hdr.append(("TRANSTAR", transit_start, "Start index of transit."))
            hdr.append(("TRANWID", transit_width, "Width of transit."))
        # This builds the primary header, no data, just keywords.
        primary_hdu = fits.PrimaryHDU(header=hdr)
        # This sets up the binary table and creates the first extension header.
        col1 = fits.Column(name="time", array=times, format='D')
        col2 = fits.Column(name="flux", array=fluxes_with_noise, format='D')
        col3 = fits.Column(name="flux_pure", array=fluxes, format='D')
        hdu1 = fits.BinTableHDU.from_columns([col1, col2, col3])
        # If the output directory doesn't exist, create it.
        if not os.path.isdir(os.path.abspath(os.path.dirname(lc_ofile))):
            os.makedirs(os.path.dirname(os.path.abspath(lc_ofile)))
        # This combines the primary HDU and first extension header together and
        # writes to the output file.
        hdu_list = fits.HDUList([primary_hdu, hdu1])
        hdu_list.writeto(lc_ofile, overwrite=True, checksum=True)

    # Return the times and fluxes as an astropy Table so it can be directly
    # used later in a script.
    return Table([times, fluxes_with_noise, fluxes],
                 names=("time", "flux", "flux_pure"))


if __name__ == "__main__":
    # Get command-line arguments.
    INPUT_ARGS = sim_lc_setup_args().parse_args()

    simulated_lc(INPUT_ARGS.lc_type, INPUT_ARGS.lc_ofile, INPUT_ARGS.lc_length,
                 INPUT_ARGS.lc_noise, INPUT_ARGS.visualize, INPUT_ARGS.lc_yoffset,
                 INPUT_ARGS.transit_depth, INPUT_ARGS.transit_period,
                 INPUT_ARGS.transit_start, INPUT_ARGS.transit_width,
                 INPUT_ARGS.sine_amp, INPUT_ARGS.sine_period, INPUT_ARGS.flare_time,
                 INPUT_ARGS.flare_amp, INPUT_ARGS.flare_halfwidth)
