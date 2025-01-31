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

TO-BE-FINALIZED

- Update the ``ci_workflows.yml`` under ``.github/workflows/`` to
  remove any inactive branches and add your new development branch,
  under the ``push`` section towards the top of the file.

- Update the __init__.py file under the "astronify/" folder to update
  the __version__ variable to match the upcoming release version. This
  should be specified as a string.
  
- Update the version information and release date in the CITATION.cff
  file, located in the top-level directory to match the upcoming release version.

- Update the "CHANGES.rst" file to add the new version, release date,
  and summary of what's changing in this version.

- Make a final commit to the branch, doing things like double checking 
  Python versions, release dates, spell check documentation files, 
  etc. Commit the final release with: 

.. code-block:: bash

    $ git commit -m "Preparing release <version>"

- Tag the commit with the version

.. code-block:: bash

    $ git tag -a <version> -m "Release version <version>"

- Make sure the `build` package is up-to-date:

.. code-block:: bash

    $ python -m build --sdist --outdir dist .

- Twine upload.

.. code-block:: bash

    twine upload dist/<my_package*.tar.gz>
