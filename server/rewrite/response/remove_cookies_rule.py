import logging

from server.parse import HarEntryResponse
from server.config import Config


_log = logging.getLogger(__file__)


def remove_cookies_from_response(config: Config, response: HarEntryResponse) -> HarEntryResponse:
    removable = config.rewrite_rules.rule_config.removable_response_cookies
    if len(removable) == 0:
        _log.warning('The remove-cookies response rewrite rule is enabled but no '
                     'rewrite-rules.config.removable-response-cookies array is configured.')
        return response

    if len(response.cookies) == 0:
        return response

    for cookie in removable:
        if cookie not in response.cookies:
            continue
        response.cookies.pop(cookie)
    return response
