import logging

from server.parse import HarEntryRequest
from server.config import Config


_log = logging.getLogger(__file__)


def remove_cookie_from_request(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_cookies(config, request)


def remove_cookie_from_entry_request(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_cookies(config, request)


def _remove_cookies(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    removable = config.rewrite_rules.rule_config.removable_request_cookies
    if len(removable) == 0:
        _log.warning('The remove-cookies request rewrite rule is enabled but no '
                     'rewrite-rules.config.removable-cookies array has been configured.')
        return request

    if len(request.cookies) == 0:
        return request

    for cookie in removable:
        if cookie not in request.cookies:
            continue
        request.cookies.pop(cookie)
    return request
