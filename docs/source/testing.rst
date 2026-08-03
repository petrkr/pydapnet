Testing
=======

PyDapnet uses pytest with mocked HTTP responses.

Test Reports
------------

The following reports can be generated during documentation builds:

* :doc:`test_results` - Detailed test execution report (pass/fail status, duration, assertions, tracebacks)
* :doc:`coverage` - Code coverage analysis (overall percentage, per-module breakdown, line-by-line visualization)

Running Tests Locally
----------------------

Prerequisites
~~~~~~~~~~~~~

Install development dependencies::

    pip install -r requirements-dev.txt

Running the Full Test Suite
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run all tests with coverage::

    python -m pytest tests/ -v --cov=dapnet --cov-report=html

This will:

* Execute all unit tests
* Generate coverage report in ``htmlcov/``
* Show coverage summary in terminal

Test Organization
-----------------

Test Structure
~~~~~~~~~~~~~~

Tests are currently kept in one file::

    tests/
    └── test_client.py

Testing Strategy
~~~~~~~~~~~~~~~~

Tests replace ``dapnet.api.requests`` with a fake request object and verify:

* generated URLs
* JSON payloads
* model parsing
* login/logout state
* API error mapping

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

**Import errors**
  Ensure the package is installed in development mode::

      pip install -e .

**Coverage not generated**
  Make sure pytest-cov is installed::

      pip install pytest-cov

Contributing
------------

When contributing code:

1. Write tests for new functionality
2. Ensure existing tests pass
3. Maintain or improve coverage
4. Follow existing test patterns
5. Document public API changes
