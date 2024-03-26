# har-server
The har-server is a configurable FastAPI server with the express intention of parsing and serving content
from a series of HTTP Archive (.har) files to enable a user to download and keep an offline copy of a dynamic or
static website.

## Starting the Server
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
There are a number of configuration options available that this document will highlight. To
utilize any of these configuration options just create a `_config.yml` within the folder you are specifying
when running the server.

A sample `_config.yml` with all available configuration options available can be found in the root
of this project.

### Configuration Properties:
* `request-matching.rules` -> The sequentially executed set of predicate functions to determine if an incoming HTTP request matches a previously recorded request pulled from a har file.
    * `method` -> Match requests by HTTP method.
    * `path` -> Match requetss by path segments. (This will exclude the host/port and will fully decode the request path.)
    * `query-params` -> Match requests by their query parameters. (This will fully decode all query parameters before matching.)
    * `headers` -> Match requests by their request headers.
* `rewrite-rules.request` -> The sequentially executed set of functions to modify an incoming request or a previously recorded request pulled from a har file.
    * `remove-query-params` -> Removes query params by name from the incoming and recorded request.
      * `rewrite-rules.config.removable-query-params` -> The list of query param names (case-sensitive) to be removed from each recorded request.
    * `remove-headers` -> Removes headers by name from the incoming and recorded request.
      * `rewrite-rules.config.removable-request-headers` -> A list of header names (case-sensitive) to be removed from all incoming and recorded requests before attempting to match them.
* `rewrite-rules.response` -> The sequentially executed set of rules to modify a response from a har file before returning it to the calling Http client.
    * `localhost` -> Rewrites the host and protocol of all http:// and https:// URLs in any matched response to http://localhost:8000.
      * `rewrite-rules.config.excluded-domains` -> A list of protocol + host combinations that should be skipped by the `localhost` rewrite rule.
      * Ex: http://www.w3.org
    * `remove-headers` -> Removes response headers by the header name.
      * `rewrite-rules.config.removable-response-headers` -> A list of header names (case-sensitive) to be removed from all matched responses before returning said response.
* `rewrite-rules.config` -> Configuration values to control the behaviour of the request and response rewrite rules.
* `entry-exclusions.rules` -> A sequentially executed set of rules that will filter out entries from each har file. Entries that are excluded will never be can never be matched or returned by the running har-server.
  * `responses-with-bad-status` -> Filter out any responses that have a matching HTTP status.
    * `entry-exclusions.config.bad-statuses` -> The list of "bad" HTTP status codes to be excluded.
  * `responses-with-invalid-size` -> Filter out responses that are empty but don't have a 204 response status.
  * `duplicate-requests` -> Filter out all requests that appear to be effectively equal to another request.
* `entry-exclusions.config` -> Configuration values to control the behaviour of the exclusion rules.