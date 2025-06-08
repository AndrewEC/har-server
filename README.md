# har-server
The har-server is a configurable FastAPI server with the express intention of parsing and serving content
from a series of HTTP Archive (.har) files (HAR file) to enable a user to download and keep an offline copy of
a dynamic or static website.

## Cloning
To clone the project and the required submodules run:
> git clone --recurse-submodules https://github.com/AndrewEC/har-server.git

## Starting the Server
To run the server first execute the command: `RunScript.ps1 Install`. This will create a virtual environment, install required dependencies, and activate said virtual environment.

After running the `RunScript.ps1 Install` command the server can be launched using:
> python -m server "<path_to_har_folder>"

where `<path_to_har_folder>` needs to be replaced with the relative or absolute path to the folder where the .har files you want to serve are located. The .har files can be further nested within the subdirectories of the input directory.

By default, the server runs on port 8080 and can be accessed using the URL: http://localhost:8080/

## Configuration
There are a number of configuration options available that this document will highlight. To utilize any of these configuration options create a `_config.yml` file within the folder you are specifying when running the server.

A sample `_config.yml` with all available configuration options available can be found in the [root of this project](./_config.yml).

### Header and Query Naming Conventions
By default, the har-server will treat all header and query parameter names in the configuration and in the HAR files as case-insensitive.

### Configuration Properties:

| Property                | Rule Name                   | Rule Config                                        | Description                                                                                                                                                                                                                |
|-------------------------|-----------------------------|----------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| debug.enable-debug-logs |                             |                                                    | Enable more granular logging statements.                                                                                                                                                                                   |
| debug.log-stack-traces  |                             |                                                    | Log the full stack trace whenever an exception is thrown while the server is running.                                                                                                                                      |
| debug.open-browser      |                             |                                                    | The URL to launch in your default browser once the server has started.                                                                                                                                                     |
| request-matching.rules  |                             |                                                    | The sequentially executed set of predicate functions to determine if an incoming HTTP request matches a previously recorded request pulled from a har file.                                                                |
|                         | method                      |                                                    | Match requests by HTTP method.                                                                                                                                                                                             |
|                         | path                        |                                                    | Match requets by path segments. (This will exclude the host/port and will fully decode the request path.)                                                                                                                  |
|                         | query-params                |                                                    | Match requests by their query parameters. (This will fully decode all query parameters before matching.)                                                                                                                   |
|                         | headers                     |                                                    | Match requests by their request headers.                                                                                                                                                                                   |
|                         | json-body                   |                                                    | Match requests by their JSON body. This will only match requests with an application/json mime type.                                                                                                                       |
| rewrite.request.rule    |                             |                                                    | The sequentially executed set of functions to modify an incoming request or a previously recorded request pulled from a har file.                                                                                          |
|                         | remove-query-params         |                                                    | Removes query params by name from the incoming and recorded request.                                                                                                                                                       |
|                         |                             | rewrite.request.config.removable-query-params      | The list of query param names (case-insensitive) to be removed from each recorded request.                                                                                                                                 |
|                         | remove-headers              |                                                    | Removes headers by name from the incoming and recorded request.                                                                                                                                                            |
|                         |                             | rewrite.request.config.removable-request-headers   | A list of header names (case-insensitive) to be removed from all incoming and recorded requests before attempting to match them.                                                                                           |
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


### A Note on Response Headers
The underlying FastAPI server, that har-server is built on top of, has logic to automatically populate select response headers such as the content-type, content-length, and content-encoding. The headers automatically added can conflict with the headers of the same name that are part of the response recorded in a HAR file.

To avoid this issue you may need to create a _config.yml file in the root of the Http Archive folder with a configuration like what is provided in the [_config_min.yml](./_config_min.yml) sample. The configuration provided in the sample YAML file will force the har-server to exclude the problematic headers from the Http Archive response entry and will only return the headers automatically set by the FastAPI server.


## Quality Metrics

Various quality metrics can be gathered by running the `RunScript.ps1 All` script. 

This build script will ensure the proper virtual environment is active, install dependencies, run unit tests with code coverage assertions, flake8, and perform dependency audits.
