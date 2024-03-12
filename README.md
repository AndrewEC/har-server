# har-server
The har-server is a configurable FastAPI server with the express intention of parsing and serving content
from a series of HTTP Archive (.har) files.

## Running
To run the server first execute the `CreateVenv.ps1` script. This will create a virtual environment, install
the required dependencies, and activate said virtual environment.

After running the `CreateVenv.ps1` script the server can be launched using:
> python -m server "<path_to_har_folder>"

where `<path_to_har_folder>` should be replaced with the relative or absolute path to the folder where the .har files
you want to serve are located.

This expects that all har files be in the root of the folder. It will not currently look through nested directories
for other folders and har files.

## Configuration
There are a number of configuration options available to alter the way the server matches requests and serves
content. To add any custom configuration you simply need to add a `_config.yml` file to the root of the
`<path_to_har_folder>` folder specified when starting the server.

A sample `_config.yml` can be found at the root of this project.
