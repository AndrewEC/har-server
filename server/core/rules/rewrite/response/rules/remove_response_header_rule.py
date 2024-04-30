import logging

from server.core.har import HarEntryResponse
from server.core.config import ConfigLoader
from server.core.config.models import ResponseRuleConfig


_log = logging.getLogger(__file__)


def remove_headers_from_response(config: ConfigLoader, response: HarEntryResponse) -> HarEntryResponse:
    removable_headers = config.read_config(ResponseRuleConfig).removable_headers
    if len(removable_headers) == 0:
        _log.warning('The remove-headers response rewrite rule is enabled but no '
                     'removable-headers have been configured.')
        return response

    if len(response.headers) == 0:
        return response

    for removable in removable_headers:
        if removable not in response.headers:
            continue
        response.headers.pop(removable)
    return response
