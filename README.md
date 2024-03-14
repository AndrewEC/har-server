# har-server
The har-server is a configurable FastAPI server with the express intention of parsing and serving content
from a series of HTTP Archive (.har) files to enable a user to download and keep an offline copy of a dynamic or
static website.

## Running
To run the server first execute the `CreateVenv.ps1` script. This will create a virtual environment, install
the required dependencies, and activate said virtual environment.

After running the `CreateVenv.ps1` script the server can be launched using:
> python -m server "<path_to_har_folder>"

where `<path_to_har_folder>` should be replaced with the relative or absolute path to the folder where the .har files
you want to serve are located.

This expects that all har files be in the root of the folder. It will not currently look through nested directories
for other folders and har files.

By default, the server runs on port 8000 and can be accessed using http://localhost:8000/

## Configuration
There are a number of configuration options available that this document will explain in the next few sections. To
utilize any of these configuration options just create a `_config.yml` within the folder you are specifying
when running the server.

A sample `_config.yml` with all available configuration options available can be found in the root
of this project.

### Configuration Properties:
* `rewrite-rules.request` -> The sequentially executed set of functions to modify an incoming request or a previously recorded request pulled from a har file.
* `request-matching.rules` -> The sequentially executed set of rules to match an incoming HTTP request to a previously recorded request loaded from a har file.
* `rewrite-rules.response` -> The sequentially executed set of rules to modify a response from a har file before returning it to the calling Http client.
* `rewrite-rules.config` -> Configuration values to control the behaviour of the request and response rewrite rules.
* `entry-exclusions.rules` -> A sequentially executed set of rules that will filter out entries from each har file.
* `entry-exclusions.config` -> Configuration values to control the behaviour of the exclusion rules.