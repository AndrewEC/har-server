Testing
=======

.. toctree::
   :maxdepth: 4


To run the full suite of unit and mutation tests simply run the **CreateVenv.ps1** script the run the build script via::

    python build.py


This build script, in addition to the running the unit and mutation tests, will also generate coverage reports,
install required dependencies, ensure a proper virtual environment is active, generate Sphinx docs, and run Flake8.

Separate mutation and unit test coverage reports will be generated at the following locations:

* Unit Tests - html/index.html
* Mutation Tests - html/index.html
