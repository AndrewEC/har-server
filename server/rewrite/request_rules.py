from typing import Callable, Dict, Tuple
import copy

from server.parse import HarEntryRequest
from server.config import Config

from .request import (remove_query_param_from_request, remove_query_param_from_entry_request,
                      remove_header_from_request, remove_header_from_entry_request)
from .errors import RequestRuleNotFoundException


_REQUEST_REWRITE_RULES: Dict[str, Tuple[Callable[[Config, HarEntryRequest], HarEntryRequest], Callable[[Config, HarEntryRequest], HarEntryRequest]]] = {
    'remove-query-params': (remove_query_param_from_request, remove_query_param_from_entry_request),
    'remove-headers': (remove_header_from_request, remove_header_from_entry_request)
}


def _get_request_rewrite_rule(name: str) -> Tuple[Callable[[Config, HarEntryRequest], HarEntryRequest], Callable[[Config, HarEntryRequest], HarEntryRequest]]:
    if name not in _REQUEST_REWRITE_RULES:
        raise RequestRuleNotFoundException(name)
    return _REQUEST_REWRITE_RULES[name]


def _apply_request_rewrite_rules(config: Config, request: HarEntryRequest, index: int) -> HarEntryRequest:
    rules = config.rewrite_rules.request_rules
    if len(rules) == 0:
        return request

    request_copy = copy.deepcopy(request)
    for rule in rules:
        request_copy = _get_request_rewrite_rule(rule)[index](config, request_copy)
    return request_copy


def apply_browser_request_rewrite_rules(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _apply_request_rewrite_rules(config, request, 0)


def apply_entry_request_rewrite_rules(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _apply_request_rewrite_rules(config, request, 1)
