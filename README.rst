pydapnet
========

Python client library for the DAPNET REST API.

Documentation: https://petrkr.github.io/pydapnet/

The current implementation targets the production DAPNET API 1.1.x exposed by
``https://hampager.de/api``.

Installation
------------

.. code-block:: console

   pip install pydapnet

Example
-------

.. code-block:: python

   from dapnet.api import DapnetApi

   api = DapnetApi()
   api.login("call", "secret")

   api.post_news(
       rubric_name="example",
       text="Hello from pydapnet",
       position=1,
   )

Status
------

Alpha. API may change before 1.0.
