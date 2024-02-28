***********************
Astronify Documentation
***********************

Introduction
============

Astronify contains tools for sonifying astronomical data. Currently Astronify can sonify data series. This package is under active development, and will ultimately grow to encompass a range of sonification functionality. 


Data Series Sonification
========================

Data series sonification refers to taking a data table and mapping one column to
time, and one column to pitch. In astronomy this technique is commonly used to
sonify light curves, where observation time is scaled to listening time
and flux is mapped to pitch. While Astronify's sonification uses the columns "time"
and "flux" by default, any two columns can be supplied and a sonification created.


Basic Usage
-----------

At base, all that is required to make a sonification is an `~astropy.table.Table` with
two columns. By default these columns are assumed to be named "time" and "flux", but
alternate column names can also be provided (see `~astronify.series.SoniSeries`).

.. code-block:: python

                >>> from astronify.series import SoniSeries
                >>> from astropy.table import Table

                >>> data_table = Table({"time":[0, 1, 2, 3, 4, 5, 9, 10, 11, 12],
                ...                     "flux": [0.3, 0.4, 0.3, 0.5, 0.5, 0.4, 0.3, 0.2, 0.3, 0.1]})

                >>> data_soni = SoniSeries(data_table)
                >>> data_soni.note_spacing = 0.2
                >>> data_soni.sonify()
                >>> data_soni.play()   #doctest: +SKIP


The default note spacing (median time between notes in seconds) is 0.01, so for short data series
we need to slow it down to hear all the data points.

This more interesting example sonifies real data from the Kepler space telescope.
The package `Lightkurve <https://docs.lightkurve.org/>`_ is used to download a Kepler
light curve and then sonify it.


.. code-block:: python
   
                >>> from astronify.series import SoniSeries
                >>> import lightkurve    #doctest: +SKIP

                >>> kep12b_lc = lightkurve.search_lightcurvefile("KIC 11804465", cadence="long", quarter=1).download_all()[0].SAP_FLUX.to_table()    #doctest: +SKIP
                >>> kep12b_obj = SoniSeries(kep12b_lc)    #doctest: +SKIP
                >>> kep12b_obj.sonify()    #doctest: +SKIP
                >>> kep12b_obj.play()   #doctest: +SKIP

                
A variety of arguments can be set to change the parameters of the sonification. You can control note spacing, note duration (each data point will get a note of the same duration),
and change a number of aspects of the algorithm used to transform data values into pitches.

.. code-block:: python

                >>> from astronify.series import SoniSeries
                >>> import lightkurve    #doctest: +SKIP

                >>> kep12b_lc = lightkurve.search_lightcurvefile("KIC 11804465", cadence="long", quarter=1).download_all()[0].SAP_FLUX.to_table()    #doctest: +SKIP
                >>> kep12b_obj = SoniSeries(kep12b_lc)    #doctest: +SKIP
                >>> kep12b_obj.pitch_mapper.pitch_map_args["center_pitch"] = 880    #doctest: +SKIP
                >>> kep12b_obj.sonify()    #doctest: +SKIP
                >>> kep12b_obj.play()   #doctest: +SKIP

                
See `~astronify.utils.data_to_pitch` for a full list of the parameters that can be changed in the
default pitch mapping function. The default pitch mapping function can also be replaced with
a user supplied function, see `~astronify.series.PitchMap` for the requirements on this function.
                 

Sonification Algorithm
----------------------
                
While the user can supply any function they like to transform data values in to pitch in Hz,
the default function for Astronify is `~astronify.utils.data_to_pitch` which takes in an array
of float values and transformed them into audible pitch values (in Hz).

**The algorithm  is as follows:**

Given a center pitch, zero point, and pitch range, the data values will be scaled with a
chosen stretch (linear, hyperbolic sine, hyperbolic arcsine, logarithmic or square
root) such that the zero point maps to the center pitch and all pitches fall within
the pitch range. The given pitch range defines the maximum pitch boundaries, but
depending on the parameters of sonification output pitches may not reach the edges.

The zero point is calculated based on the input argument (mean, median, or specified value)
and then appended to the data array. The resulting array is scaled to the interval [0,1]
taking into account any requested clipping, and the requested stretch is applied. At this point
if the invert argument is set, the array is inverted by subtracting all values from 1.

The scaled zero point is then removed from the array which is scaled to the pitch range
such that the scaled zero point becomes the center pitch value and the entire pitch range
falls within the input pitch range. In practice this means one of two things:
The array is scaled such that the 0 corresponds to the minimum of the input pitch range and the
scaled zero point corresponds to the center pitch value. Or, the scaled zero point corresponds to
the center pitch value and 1 corresponds to the maximum of the input pitch range. Whichever
scaling means that all output pitch values fall within the desired range.


Troubleshooting
---------------

This package is still in beta and as such may not be completely stable.
If you encounter problems please open a
`github issue <https://github.com/spacetelescope/astronify/issues>`_. We
also welcome code contributions in the form of pull requests.

The following are known issues/troubleshooting tips:

    - Sonifications cease playing when running in a Jupyter notebook—        
      Restart the kernel, particularly if it has been running for a while.

    - Sonification will not play when run in a script—    
      Currently sonifications cannot be played (using the `.play()` method from
      python scripts (as opposed to in interactive mode). Instead write the
      sonification to a file and play the result in the audio player of your choice.
  


Light Curve Simulator
=====================

Astronify also provides a simulation package for creating synthetic light
curves with various characteristics that can then be sonified. The main
function is `~astronify.simulator.simulated_lc` which allows the user to
create a light curve that is flat, sinusoidal, or contains a transiting
exoplanet or stellar flare.

.. code-block:: python

                >>> from astronify import simulator, series

                >>> lc_data = simulator.simulated_lc("transit", visualize=False, transit_depth=1.5,
                ...                                   transit_period=145, transit_width=42,
                ...                                   lc_noise=0.5, lc_length=750)
                >>> soni_obj = series.SoniSeries(lc_data)
                >>> soni_obj.sonify()
                >>> soni_obj.play()   #doctest: +SKIP
