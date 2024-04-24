import logging

from server.parse import HarEntryRequest
from server.config import Config


_log = logging.getLogger(__file__)


def remove_query_param_from_request(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_params(config, request)


def remove_query_param_from_entry_request(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _remove_params(config, request)


def _remove_params(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    removable = config.rewrite_rules.rule_config.removable_query_params
    if len(removable) == 0:
        _log.warning('The remove-query-params request rewrite rule is enabled but no '
                     'rewrite-rules.config.removable-query-params array has been configured.')
        return request

    if len(request.query_params) == 0:
        return request

    for param in removable:
        if param not in request.query_params:
            continue
        request.query_params.pop(param)
    return request
