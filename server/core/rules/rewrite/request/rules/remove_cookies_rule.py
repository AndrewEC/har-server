import logging

from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader
from server.core.config.models import RequestRewriteConfig


_log = logging.getLogger(__file__)


def remove_cookie_from_request(config: ConfigLoader, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_cookies(config, request)


def remove_cookie_from_entry_request(config: ConfigLoader, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_cookies(config, request)


def _remove_cookies(config: ConfigLoader, request: HarEntryRequest) -> HarEntryRequest:
    removable = config.read_config(RequestRewriteConfig).removable_cookies
    if len(removable) == 0:
        _log.warning('The remove-cookies request rewrite rule is enabled but no '
                     'removable-cookies have been configured.')
        return request

    if len(request.cookies) == 0:
        return request

    for cookie in removable:
        if cookie not in request.cookies:
            continue
        request.cookies.pop(cookie)
    return request
