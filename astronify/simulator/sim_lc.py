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
import sim_lc_config
from add_flare_signal import add_flare_signal
from add_lc_noise import add_lc_noise
from add_sine_signal import add_sine_signal
from add_transit_signal import add_transit_signal
from check_transit_params import check_transit_params
from sim_lc_setup_args import sim_lc_setup_args

def sim_lc(lc_type, lc_ofile=sim_lc_config.sim_lc_ofile,
           lc_length=sim_lc_config.sim_lc_length,
           lc_noise=sim_lc_config.sim_lc_noise,
           visualize=sim_lc_config.sim_lc_visualize,
           lc_yoffset=sim_lc_config.sim_lc_yoffset,
           transit_depth=sim_lc_config.sim_lc_transit_depth,
           transit_period=sim_lc_config.sim_lc_transit_period,
           transit_start=sim_lc_config.sim_lc_transit_start,
           transit_width=sim_lc_config.sim_lc_transit_width,
           sine_amp=sim_lc_config.sim_lc_sine_amp,
           sine_period=sim_lc_config.sim_lc_sine_period):
    """
    Create light curve of specified type as a FITS file.

    :param lc_type: Type of light curve to make.
    :type lc_type: str

    :param lc_ofile: Name of output FITS file.  If set to an empty string,
    no file will be saved to disk.
    :type lc_ofile: str

    :param lc_length: Number of fluxes in light curve.
    :type lc_length: int

    :param lc_noise: Standard deviation of normal distribution to draw from when
    adding noise, a value of zero means no noise is added.
    :type lc_noise: float

    :param visualize: If True, plot the light curve being made to the screen.
    :type visualize: bool

    :param lc_yoffset: Baseline flux level (unitless).
    :type lc_yoffset: float

    :param transit_depth: Depth of transit, as a percent (e.g., 10.0 = 10%.)
    :type transit_depth: float

    :param transit_period: Period of transit (number of fluxes/bins between
    the start of each event.)
    :type transit_period: int

    :param transit_start: Start index of transit (the index of the flux/bin to
    use as the start of the first transit event.)
    :type transit_start: int

    :param transit_width: Width of transit (number of fluxes/bins between
    the start and end of each event.)
    :type transit_width: int

    :param sine_amp: Amplitude of the sinusoidal signal to add.
    :type sine_anp: float

    :param sine_period: Period of the sinusoidal signal to add.
    :type sine_period: float

    :returns: astropy Table -- The time and flux columns.
    """

    # Generate baseline light curve fluxes.
    fluxes = np.full(lc_length, lc_yoffset)

    # We don't need real times for the simulation, it's just an array of indexes.
    times = np.arange(fluxes.size)

    # Apply signal of choice if needed.
    if lc_type == "flare":
        # TO-DO: Enable this function, doesn't add anything yet.
        fluxes = add_flare_signal(fluxes)
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
        # This builds the primary header, no data, just keywords.
        primary_hdu = fits.PrimaryHDU(header=hdr)
        # This sets up the binary table and creates the first extension header.
        col1 = fits.Column(name="time", array=times, format='D')
        col2 = fits.Column(name="flux", array=fluxes_with_noise, format='D')
        col3 = fits.Column(name="flux_pure", array=fluxes, format='D')
        hdu1 = fits.BinTableHDU.from_columns([col1, col2, col3])
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

    sim_lc(INPUT_ARGS.lc_type, INPUT_ARGS.lc_ofile, INPUT_ARGS.lc_length,
           INPUT_ARGS.lc_noise, INPUT_ARGS.visualize, INPUT_ARGS.lc_yoffset,
           INPUT_ARGS.transit_depth, INPUT_ARGS.transit_period,
           INPUT_ARGS.transit_start, INPUT_ARGS.transit_width,
           INPUT_ARGS.sine_amp, INPUT_ARGS.sine_period)
