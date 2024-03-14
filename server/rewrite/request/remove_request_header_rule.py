import logging

from server.parse import HarEntryRequest
from server.config import Config


_log = logging.getLogger(__file__)


def remove_header_from_request(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_header_from_request(config, request)


def remove_header_from_entry_request(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_header_from_request(config, request)


def _remove_header_from_request(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    removable_headers = config.rewrite_rules.rule_config.removable_headers
    if len(removable_headers) == 0:
        _log.info('The remove-request-headers request rewrite rule is enabled but no '
                  'rewrite-rules.config.removable-request-headers array has been configured.')
        return request

    for removable in removable_headers:
        if removable not in request.headers:
            continue
        request.headers.pop(removable)
    return request
