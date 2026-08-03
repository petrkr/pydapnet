Installation
============

PyDapnet is a small Python client for the production DAPNET REST API 1.1.x.

CPython
--------

Install from PyPI::

   pip install pydapnet

Install from source in a virtual environment::

   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .

MicroPython
-----------

Release tags build MicroPython artifacts automatically:

* ``pydapnet-<version>-mip.json`` for ``mip``
* ``pydapnet-<version>-mpy-<micropython-version>.tar`` with precompiled
  ``.mpy`` files

Install from a release with ``mip``::

   import mip
   mip.install("https://github.com/petrkr/pydapnet/releases/download/v0.0.1/pydapnet-0.0.1-mip.json")

Or unpack the matching ``.mpy`` tar archive from the GitHub release and upload
the ``dapnet`` directory to the device.
