|Property|Rule Name|Rule Config|Description|
|---|---|---|---|
|port|||The port to start the server on.|
|open-browser|||The URL to launch in your default browser once the server has started. URLs can use {port} as a placeholder value that will be substituted with the real port at runtime.|
|debug.enable-debug-logs|||Enable more granular logging statements.|
|debug.log-stack-traces|||Log the full stack trace whenever an exception is thrown while the server is running.|
|debug.enable-metrics|||Enables recording information about which requests match to which entries. Once enable metrics can be retrieved using the GET /__metrics__ endpoint.|
|request-matching.rules|||The sequentially executed set of predicate functions to determine if an incoming HTTP request matches a previously recorded request pulled from a har file.|
||method||Match requests by HTTP method.|
||path||Match requests by path segments. (This will exclude the host/port and will fully decode the request path.)|
||query-params||Match requests by their query parameters. (This will fully decode all query parameters before matching.)|
||headers||Match requests by their request headers.|
||cookies||Match requests by their cookies.|
||body||Match requests by their body. This only supports application/json and application/x-www-form-urlencoded formats.|
|rewrite.request.rules|||The sequentially executed set of functions to modify an incoming request or a previously recorded request pulled from a har file. By default these rules are executed each time an incoming request is processed.|
||remove-query-params||Removes query params by name from the incoming and recorded request.|
|||rewrite.request.config.removable-query-params|The list of query param names (case-insensitive) to be removed from each recorded request.|
||remove-headers||Removes headers by name from the incoming and recorded request.|
|||rewrite.request.config.removable-request-headers|A list of header names (case-insensitive) to be removed from all incoming and recorded requests before attempting to match them.|
||remove-cookies||Removes cookies by name from the incoming and recorded request.|
|||rewrite.request.config.removable-request-cookies|The list of cookie names (case-insensitive) to be removed from each request.|
|rewrite.response.rules|||The sequentially executed set of rules to modify a response from a har file before returning it to the calling Http client.|
||urls-in-response||Rewrites the host and protocol of all `http://` and `https://` URLs in any matched response to `http://localhost:${server.port}` where `${server.port}` will be replaced with the port the server is currently running on.|
|||rewrite.response.config.excluded-domains|A list of protocol + host combinations that should be skipped by the `urls-in-response` rewrite rule. Ex: `http://www.w3.org` or `http://www.w3.org:8080`. This also supports blank protocols such as `//www.w3.org`.|
||remove-headers||Removes response headers by the header name.|
|||rewrite.response.config.removable-response-headers|A list of header names (case-insensitive) to be removed from all matched responses before returning said response.|
||remove-cookies||Removes response cookies by the cookie name.|
|||rewrite.response.config.removable-cookies|A list of cookie names (case-insensitive) to be removed from all matched responses before returning said response.|
||remove-html-script-tags||Remove all &lt;script&gt; tags from any response content that has a mimetype containing text/html.|
||remove-integrity-attribute||"Remove the ""integrity"" attribute from script and link tags in any response content that has a mimetype containing text/html."|
|exclusions.rules|||A sequentially executed set of rules that will filter out entries from each har file. Entries that are excluded will never be can never be matched or returned by the running har-server. By default the rules will be executed during the processing of every incoming HTTP request.|
||responses-with-status||Filter out any responses that have a matching HTTP status.|
|||exclusions.config.removable-statuses|The list of HTTP status codes to be excluded.|
||responses-with-invalid-size||Exclude HAR entries that have an empty response body but don't have a 204 response status.|
||requests-with-http-method||Exclude HAR entries that have a request with a specific HTTP verb.|
|||exclusions.config.removable-http-methods|The list of HTTP methods to be excluded.|
||requests-with-matching-url||Exclude HAR entries that have a request with a URL matching one of the provided regular expressions.|
|||exclusions.config.removable-url-expressions|The list of regular expressions to match request URLs by.|
