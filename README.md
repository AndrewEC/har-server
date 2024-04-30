# har-server
The har-server is a configurable FastAPI server with the express intention of parsing and serving content
from a series of HTTP Archive (.har) files to enable a user to download and keep an offline copy of a dynamic or
static website.

## Starting the Server
To run the server first execute the `CreateVenv.ps1` script. This will create a virtual environment, install
required dependencies, and activate said virtual environment.

After running the `CreateVenv.ps1` script the server can be launched using:
> python -m server "<path_to_har_folder>"

where `<path_to_har_folder>` should be replaced with the relative or absolute path to the folder where the .har files
you want to serve are located. The .har files can be further nested within the subdirectories of the input
directory.

By default, the server runs on port 8080 and can be accessed using http://localhost:8080/

## Configuration
There are a number of configuration options available that this document will highlight. To
utilize any of these configuration options create a `_config.yml` file within the folder you are specifying
when running the server.

A sample `_config.yml` with all available configuration options available can be found in the [root
of this project](./_config.yml).

### Configuration Properties:

| Property                | Rule Name                   | Rule Config                                        | Description                                                                                                                                                                                                                |
|-------------------------|-----------------------------|----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| debug.enable-debug-logs |                             |                                                    | Enable more granular logging statements.                                                                                                                                                                                   |
| debug.dump-urls         |                             |                                                    | Dump the URLs loaded from the .har files after all exclusion rules have been executed.                                                                                                                                     |
| debug.log-stack-traces  |                             |                                                    | Log the full stack trace whenever an exception is thrown while the server is running.                                                                                                                                      |
| debug.open-browser      |                             |                                                    | The URL to launch in your default browser once the server has started.                                                                                                                                                     |
| request-matching.rules  |                             |                                                    | The sequentially executed set of predicate functions to determine if an incoming HTTP request matches a previously recorded request pulled from a har file.                                                                |
|                         | method                      |                                                    | Match requests by HTTP method.                                                                                                                                                                                             |
|                         | path                        |                                                    | Match requets by path segments. (This will exclude the host/port and will fully decode the request path.)                                                                                                                  |
|                         | query-params                |                                                    | Match requests by their query parameters. (This will fully decode all query parameters before matching.)                                                                                                                   |
|                         | headers                     |                                                    | Match requests by their request headers.                                                                                                                                                                                   |
| rewrite.request.rule    |                             |                                                    | The sequentially executed set of functions to modify an incoming request or a previously recorded request pulled from a har file.                                                                                          |
|                         | remove-query-params         |                                                    | Removes query params by name from the incoming and recorded request.                                                                                                                                                       |
|                         |                             | rewrite.request.config.removable-query-params      | The list of query param names (case-insensitive) to be removed from each recorded request.                                                                                                                                 |
|                         | remove-headers              |                                                    | Removes headers by name from the incoming and recorded request.                                                                                                                                                            |
|                         |                             | rewrite.request.config.removable-request-headers   | A list of header names (case-sensitive) to be removed from all incoming and recorded requests before attempting to match them.                                                                                             |
|                         | remove-cookies              |                                                    | Removes cookies by name from the incoming and recorded request.                                                                                                                                                            |
|                         |                             | rewrite.request.config.removable-request-cookies   | The list of cookie names (case-insensitive) to be removed from each request.                                                                                                                                               |
| rewrite.response.rule   |                             |                                                    | The sequentially executed set of rules to modify a response from a har file before returning it to the calling Http client.                                                                                                |
|                         | urls-in-response            |                                                    | Rewrites the host and protocol of all `http://` and `https://` URLs in any matched response to `http://localhost:${server.port}` where `${server.port}` will be replaced with the port the server is currently running on. |
|                         |                             | rewrite.response.config.excluded-domains           | A list of protocol + host combinations that should be skipped by the `urls-in-response` rewrite rule. Ex: `http://www.w3.org`. This also supports blank protocols such as `//www.w3.org`.                                  |
|                         | remove-headers              |                                                    | Removes response headers by the header name.                                                                                                                                                                               |
|                         |                             | rewrite.response.config.removable-response-headers | A list of header names (case-insensitive) to be removed from all matched responses before returning said response.                                                                                                         |
|                         | remove-cookies              |                                                    | Removes response cookies by the cookie name.                                                                                                                                                                               |
|                         |                             | rewrite.response.config.removable-cookies          | A list of cookie names (case-insensitive) to be removed from all matched responses before returning said response.                                                                                                         |
| rewrite.request.config  |                             |                                                    | Configuration values to control the behaviour of the request and response rewrite rules.                                                                                                                                   |
| exclusions.rules        |                             |                                                    | A sequentially executed set of rules that will filter out entries from each har file. Entries that are excluded will never be can never be matched or returned by the running har-server.                                  |
|                         | responses-with-status       |                                                    | Filter out any responses that have a matching HTTP status.                                                                                                                                                                 |
|                         |                             | exclusions.config.removable-statuses               | The list of "bad" HTTP status codes to be excluded.                                                                                                                                                                        |
|                         | responses-with-invalid-size |                                                    | Filter out responses that are empty but don't have a 204 response status.                                                                                                                                                  |
| exclusions.config       |                             |                                                    | Configuration values to control the behaviour of the exclusion rules.                                                                                                                                                      |