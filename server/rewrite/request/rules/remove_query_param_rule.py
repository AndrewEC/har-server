import logging

from server.har import HarEntryRequest
from server.config import ConfigLoader
from server.config.models import RequestRewriteConfig


_log = logging.getLogger(__file__)


def remove_query_param_from_request(config: ConfigLoader, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_params(config, request)


def remove_query_param_from_entry_request(config: ConfigLoader, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_params(config, request)


def _remove_params(config: ConfigLoader, request: HarEntryRequest) -> HarEntryRequest:
    removable = config.read_config(RequestRewriteConfig).removable_query_params
    if len(removable) == 0:
        _log.warning('The remove-query-params request rewrite rule is enabled but no '
                     'removable-query-params have been configured.')
        return request

    if len(request.query_params) == 0:
        return request

    for param in removable:
        if param not in request.query_params:
            continue
        request.query_params.pop(param)
    return request
