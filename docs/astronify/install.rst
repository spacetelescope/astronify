************
Installation
************

  
Installing astronify
====================

Using pip
---------

The easiest way to install Astronify is using pip::

    pip install astronify

Errors installing dependent packages
------------------------------------

You may experience difficulties installing Astronify without some
libraries pre-installed.  If you run into problems, we recommend
installing the following dependencies of `pyo` prior to running the
`pip install astronify` step.

Mac
~~~
We recommend installing `homebrew` (https://brew.sh) and then running::

  brew install portaudio portmidi libsndfile liblo

Still having issues?
^^^^^^^^^^^^^^^^^^^^
If you are still unable to install `astronify` (or `pyo`) via `pip`,
it's possible `pip` is looking for them in the wrong spot, depending on
how you've installed other packages in your envionrment.  If so, try
adding the following flags to your shell of choice, open a new
terminal, and then run `pip install astronify` again::

  # Example for .cshrc
  setenv CFLAGS '-I/opt/homebrew/include/'
  setenv LDFLAGS '-L/opt/homebrew/lib/'

  # Example for .bashrc
  export CFLAGS="-I/opt/homebrew/include/"
  export LDFLAGS="-L/opt/homebrew/lib/"

Linux
~~~~~
We recommend installing the following with apt-get::

  apt-get install portaudio19-dev libsndfile1-dev libportmidi-dev liblo-dev

From source
-----------

To install the bleeding edge version from github without downloading,
run the following command::

  pip git+https://github.com/spacetelescope/astronify.git

The latest development version of astrocut can be cloned from github
using this command::

    git clone https://github.com/spacetelescope/astronify.git

To install astrocut (from the root of the source tree)::

    pip install .

   
