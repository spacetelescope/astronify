***********************
Astronify Documentation
***********************

Introduction
============

Astronify contains tools for sonifying astronomical data. This package is under
active development, and will ultimately grow to encompass a range of sonification
functionality. Currently only data series sonification is available.


Data Series Sonification
========================

Data series sonification refers to taking a data table and mapping one column to
time, and one column to pitch. In astronomy this technique is commonly used to
sonify light curves, where time is mapped to time (scaled for reasonable listening)
and flux is mapped to pitch. While Astronify's sonification uses the columns "time"
and "flux" by default, any two columns can be supplied and a sonification created.


Basic Usage
-----------

At base, all that is required to make a sonification is an `~astropy.table.Table` with
two columns. By default these columns are assumes to be named "time" and "flux", but
altername column names can also be provided (see `~astronify.series.SoniSeries`).

.. code-block:: python

                >>> from astronify.series import SoniSeries
                >>> from astropy.table import Table

                >>> data_table = Table({"time":[0, 1, 2, 3, 4, 5, 9, 10, 11, 12],
                ...                     "flux": [0.3, 0.4, 0.3, 0.5, 0.5, 0.4, 0.3, 0.2, 0.3, 0.1]})

                >>> data_soni = SoniSeries(data_table)
                >>> data_soni.note_spacing = 0.2
                >>> data_soni.sonify()
                >>> data_soni.play()


The default note spacing (median tiem between notes in seconds) is 0.01, so for short data series
we need to slow it down to hear all the data points.

A more interesting example sonifies real data from the Kepler space telescope.
This example uses the package `Lightkurve <https://docs.lightkurve.org/>`_ to download a Kepler
light curve and then sonify it.

.. code-block:: python

                >>> from astronify.series import SoniSeries
                >>> import lightkurve

                >>> kep12b_lc = lightkurve.search_lightcurvefile("KIC 11804465", cadence="long", quarter=1).download_all()[0].SAP_FLUX.to_table()
                >>> kep12b_obj = SoniSeries(kep12b_lc)
                >>> kep12b_obj.sonify()
                >>> kep12b_obj.play()

                
A variety of arguments can be set to change the parameters of the sonification. As well as note
spacing, you can also control the note duration (each data point will get a note of the same duration),
as well as changing a number of aspects of the algorithm used to transform data dalues into pitches.

.. code-block:: python

                >>> from astronify.series import SoniSeries
                >>> import lightkurve

                >>> kep12b_lc = lightkurve.search_lightcurvefile("KIC 11804465", cadence="long", quarter=1).download_all()[0].SAP_FLUX.to_table()
                >>> kep12b_obj = SoniSeries(kep12b_lc)
                >>> kep12b_obj.pitch_mapper.pitch_map_args["center_pitch"] = 880
                >>> kep12b_obj.sonify()
                >>> kep12b_obj.play()

                
See `~astronify.utils.data_to_pitch` for a full list of the parameters that can be changed in the
default pitch mapping function. The defualt pitch mapping function can also be replaced with
a user supplied function, see `~astronify.series.PitchMap` for the requirements on this function.
                 

Sonification Algorithm
----------------------
                
While the use can suply any function they like to transform data values in to pitch in Hz,
the default function for Astronify is `~astronify.utils.data_to_pitch` which takes in an array
of float values and transformed them into audible pitch values (in Hz).

**The algorithm  is as follows:**

Given a center pitch, zero point, and pitch range, the data values will be scaled with a
given stretch (options are linear, hyperbolic sine, hyperboic arcsine, logarithmic and square
root) such that the zero point maps to the center pitch and all pitches fall within
the pitch range (the entire pitch range may not be used).

The zero point is calculated based on the input argument (mean, median, or specified value)
and then appended to the data array. The resulting array is scaled to the interval [0,1]
taking into account any requested cipping, and the requested stretch is applied. At this point
if the invert argument is set, the array is inverted by subtracting all values from 1.

The scaled zero point is then removed from the array which is scaled to the pitch range
such that the scaled zero point become the center pitch value and the entire pitch range
falled within the input pitch range. In practice this means that the array is either scaled
such that the 0 corresponds to the minimum of the input pitch range and the scaled zero point
corresponds to the center pitch value, or the scaled zero pointcorresponds to the center pitch
value and 1 corresponds to the maximum of the input pitch range, whichever scaling means that
all output pitch values fall within the desired range.


Troubleshooting
---------------

This package is still in beta and as such may not be completely stable.
If you encounter problems please open a
`github issue <https://github.com/spacetelescope/astronify/issues>`_, and we
also welcome code contributions in the form of pull requests.

The following are known issues/troubleshooting tips:

    - Sonifications cease playing when running in a Jupyter notebook.        
      Restart the kernel. Particularly if the kernal has been running for awhile.

    - Sonification will not play wehn run in a script.    
      Currently sonifications cannot be played (using the `.play()` method from
      python scripts (as opposed to in interactive mode). Instead write the
      sonification to a file and play the result in the audio player of your choice.
  


Light Curve Simulator
=====================

Astronify also provides a simulation package for creating synthetic light
curves with various characteristics that can then be sonified. The main
function is `~astronify.simulator.simulated_lc` which allows the user to
create a light curve that is flate, sinusoidal, or contains either a transiting
exoplanet or stellar flare.

.. code-block:: python

                >>> from astronify import simulator, series

                >>> lc_data = simulator.simulated_lc("transit", visualize=Fakse, transit_depth=1.5,
                ...                                   transit_period=145, transit_width=42,
                ...                                   lc_noise=0.5, lc_length=750)
                >>> soni_obj = series.SoniSeries(lc_data)
                >>> soni_obj.sonify()
                >>> soni_obj.play()



Astronify API
=============  
        
.. automodapi:: astronify.series
    :no-inheritance-diagram:

.. automodapi:: astronify.utils
    :no-inheritance-diagram:

.. automodapi:: astronify.simulator
    :no-inheritance-diagram:

