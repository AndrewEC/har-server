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

har-server listens to port 8080 and can be accessed using the URL: http://localhost:8080/

## Configuration
A breakdown of the available properties and what they do can be found in the [Configuration Properties](./ConfigurationProperties.md) docs.

To utilize any of these configuration options create a `_config.yml` file within the folder you are specifying when running the server.

A sample `_config.yml` with all available configuration options available can be found in the [root of this project](./configs/_config.yml).

### Header and Query Naming Conventions
By default, the har-server will treat all header and query parameter names in the configuration and in the HAR files as case-insensitive.

### A Note on Response Headers
The underlying FastAPI server, that har-server is built on top of, has logic to automatically populate select response headers such as the content-type, content-length, and content-encoding. The headers automatically added can conflict with the headers of the same name that are part of the response recorded in a HAR file.

To avoid this issue you may need to create a _config.yml file in the root of the Http Archive folder with a configuration like what is provided in the [_config_min.yml](./configs/_config_min.yml) sample. The configuration provided in the sample YAML file will force the har-server to exclude the problematic headers from the Http Archive response entry and will only return the headers automatically set by the FastAPI server.


## Quality Metrics

Various quality metrics can be gathered by running the `RunScript.ps1 All` script. 

This build script will ensure the proper virtual environment is active, install dependencies, run unit tests with code coverage assertions, flake8, and perform dependency audits.
