import logging

from server.parse import HarEntryResponse
from server.config import Config


_log = logging.getLogger(__file__)


def remove_headers_from_response(config: Config, response: HarEntryResponse) -> HarEntryResponse:
    removable_headers = config.rewrite_rules.rule_config.removable_response_headers
    if len(removable_headers) == 0:
        _log.warning('The remove-headers response rewrite rule is enabled but no '
                     'rewrite-rules.config.removable-response-headers array is configured.')
        return response

    if len(response.headers) == 0:
        return response

    for removable in removable_headers:
        if removable not in response.headers:
            continue
        response.headers.pop(removable)
    return response
