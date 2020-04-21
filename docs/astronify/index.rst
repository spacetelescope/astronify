***********************
Astronify Documentation
***********************

Introduction
------------

Astronify is a package for sonifying astronomical data.

Data Series Sonification
------------------------

Here is a basic example of how to sonify an astronomical light curve.
In addition to Astronify, we will use the package `Lightkurve <https://docs.lightkurve.org/>`_ to download the data before sonification.

.. code-block:: python

                >>> import astronify
                >>> import lightkurve

                >>> kep12b_lc = lightkurve.search_lightcurvefile("KIC 11804465", cadence="long", quarter=1).download_all()[0].SAP_FLUX.to_table()
                >>> kep12b_lc = kep12b_lc[~kep12b_lc["flux"].mask]
                >>> kep12b_obj = astronify.SoniSeries(kep12b_lc)
                >>> kep12b_obj.sonify()
                >>> kep12b_obj.play()

Reference/API
=============

.. automodapi:: astronify
