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
There are a number of configuration options available to alter the way the server matches requests and serves
content. A sample `_config.yml` with all available configuration options available can be found in the root
of this project.

## Request Matching
Request matching is the act of matching an incoming request from the client browser or HTTP client with a request
recorded in one of the HTTP Archive files.

Request matching is done through a series of request matchers. The list of matchers to use can be configured
through the `request-matching.rules` array property in the config file.

The order in which the request matchers will be executed matches the order in which they are defined in the
configuration file.

By default, the server can match requests by matching:
* HTTP Method
* Request Path
* Query Parameters
* Headers

### Custom Request Matchers
A request matcher is a predicate function that takes in 3 arguments and returns a boolean value indicating if the
requests match or not.

* The first argument represents the server's current configuration.
* The second argument is a previously recorded request pulled from a har file.
* The third and final argument is the incoming request to be matched against a request from a har file.

Existing request matchers are defined in the `server.routes.match` package. All matcher source files have the
`_matcher` suffix.

The list of available matchers are configured in the `server.routes.match.match._MATCHERS` dictionary in which the
keys are the name of the matcher that can be specified in the configuration file to enable said matcher and the
value is the predicate function to be executed when the matcher is enabled.

## Rewrite Rules
Rewrite rules are rules that allow the server to modify a request or response on the fly.

Request rewrite rules consist of two separate functions in which the functions can mutate the request pulled from the
har file and the incoming request respectively.

Response rewrite rules are applied to a recorded response pulled from a har file only after the associated request
has been matched.
