Examples
========

Version
-------

.. code-block:: python

   from dapnet.api import DapnetApi

   api = DapnetApi()
   version = api.get_version()
   print(version.core, version.api)

Login
-----

.. code-block:: python

   from dapnet.api import DapnetApi

   api = DapnetApi()
   user = api.login("ok1abc", "secret")

   print(api.logged_in)
   print(api.user.admin)

Post News
---------

.. code-block:: python

   from dapnet.api import DapnetApi

   api = DapnetApi()
   api.login("ok1abc", "secret")
   api.post_news("example", "Hello from PyDapnet", position=1)

Post Call
---------

.. code-block:: python

   from dapnet.api import DapnetApi

   api = DapnetApi()
   api.login("ok1abc", "secret")
   api.post_call("Hello", "ok1abc", "ok-all")

Activate Rubrics
----------------

.. code-block:: python

   from dapnet.api import DapnetApi

   api = DapnetApi()
   api.login("ok1abc", "secret")
   api.activate_rubrics(1, "ok-all")
