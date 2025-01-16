Developer Documentation
-----------------------

This documentation is intended for code maintainers and developers as a guide, especially when preparing to merge and release a new version of the code.

Installation
^^^^^^^^^^^^

.. code-block:: bash

    $ git clone https://github.com/spacetelescope/astronify.git
    $ cd astronify
    $ pip install .

For active development, install in develop mode

.. code-block:: bash

    $ pip install -e .


Testing
^^^^^^^
Testing is run with `tox <https://tox.readthedocs.io>`_ (``pip install tox``).
Tests can be found in ``tests/`` sub-directories.

.. code-block:: bash

    $ tox -e test

Tests can also be run directly with pytest:

.. code-block:: bash

    $ pip install -e .[test]
    $ pytest
 

Documentation
^^^^^^^^^^^^^

Documentation files are found in ``docs/``.

We build the documentation with `tox <https://tox.readthedocs.io>`_ (``pip install tox``):

.. code-block:: bash

    $ tox -e build_docs

You can also build the documentation with Sphinx directly using:

.. code-block:: bash
                
    $ cd docs
    $ sphinx-build -M html . _build/
    
The built docs will be in ``docs/_build/html/``, to view them go to ``file://</path/to/astronify/repo/>docs/_build/html/index.html`` in the browser of your choice.


Release Protocol
^^^^^^^^^^^^^^^^

Coming soon.
