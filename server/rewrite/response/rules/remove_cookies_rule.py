import logging

from server.har import HarEntryResponse
from server.config import ConfigLoader
from server.config.models import ResponseRuleConfig


_log = logging.getLogger(__file__)


def remove_cookies_from_response(config: ConfigLoader, response: HarEntryResponse) -> HarEntryResponse:
    removable = config.read_config(ResponseRuleConfig).removable_cookies
    if len(removable) == 0:
        _log.warning('The remove-cookies response rewrite rule is enabled but no '
                     'removable-cookies have been configured configured.')
        return response

    if len(response.cookies) == 0:
        return response

    for cookie in removable:
        if cookie not in response.cookies:
            continue
        response.cookies.pop(cookie)
    return response
