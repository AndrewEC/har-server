Running
==========

.. toctree::
   :maxdepth: 4


To start the server first run the following script. This will create a virtual environment and
install the required dependencies::

    CreateVenv.ps1

From here the server can be started with the following command::

    python -m server <path_to_har_folder>

The <path_to_har_folder> in the above command should be replaced with the relative or absolute path to the folder
that contains one or more Http Archives (HAR). The HAR files can be nested further in other child directories
but all HAR files must have the .har extension.
