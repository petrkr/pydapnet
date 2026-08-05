API Reference
=============

PyDapnet exposes the DAPNET REST API through :class:`dapnet.api.DapnetApi`.

Overview
--------

The first release wraps read-only endpoints for main DAPNET objects and the
operational POST endpoints for news, calls, and Skyper rubric activation.

Quick Reference
---------------

.. autosummary::
   :nosignatures:

   dapnet.api.DapnetApi
   dapnet.errors.DapnetAuthError
   dapnet.errors.DapnetApiError
   dapnet.errors.DapnetNotFoundError
   dapnet.errors.DapnetPermissionError

Detailed Documentation
----------------------

.. toctree::
   :maxdepth: 2

   client
   models
   errors
