import logging

from server.har import HarEntryRequest
from server.config import ConfigLoader
from server.config.models import RequestRewriteConfig


_log = logging.getLogger(__file__)


def remove_header_from_request(config: ConfigLoader, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_header_from_request(config, request)


def remove_header_from_entry_request(config: ConfigLoader, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_header_from_request(config, request)


def _remove_header_from_request(config: ConfigLoader, request: HarEntryRequest) -> HarEntryRequest:
    removable_headers = config.read_config(RequestRewriteConfig).removable_headers
    if len(removable_headers) == 0:
        _log.info('The remove-headers request rewrite rule is enabled but no '
                  'removable-headers have been configured.')
        return request

    if len(request.headers) == 0:
        return request

    for removable in removable_headers:
        if removable not in request.headers:
            continue
        request.headers.pop(removable)
    return request
