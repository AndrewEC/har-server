from typing import Callable, Dict, Tuple
import copy

from server.parse import HarEntryRequest, HarEntryResponse
from server.config import Config

from .localhost_rule import rewrite_response_content_urls
from .strip_query_param_rule import strip_query_param_from_entry_request, strip_query_param_from_request


_RESPONSE_REWRITE_RULES: Dict[str, Callable[[Config, HarEntryResponse], HarEntryResponse]] = {
    'localhost': rewrite_response_content_urls
}

_REQUEST_REWRITE_RULES: Dict[str, Tuple[Callable[[Config, HarEntryRequest], HarEntryRequest], Callable[[Config, HarEntryRequest], HarEntryRequest]]] = {
    'strip-query-params': (strip_query_param_from_request, strip_query_param_from_entry_request)
}


class RuleNotFoundException(Exception):

    _MESSAGE_TEMPLATE = 'No {} rule with the name [{}] could be found.'

    def __init__(self, rule_type: str, name: str):
        super().__init__(RuleNotFoundException._MESSAGE_TEMPLATE.format(rule_type, name))


class ResponseRuleNotFoundException(RuleNotFoundException):

    def __init__(self, name: str):
        super().__init__('response', name)


class RequestRuleNotFoundException(RuleNotFoundException):

    def __init__(self, name: str):
        super().__init__('request', name)


def _get_request_rewrite_rule(name: str) -> Tuple[Callable[[Config, HarEntryRequest], HarEntryRequest], Callable[[Config, HarEntryRequest], HarEntryRequest]]:
    if name not in _REQUEST_REWRITE_RULES:
        raise RequestRuleNotFoundException(name)
    return _REQUEST_REWRITE_RULES[name]


def _get_response_rewrite_rule(name: str) -> Callable[[Config, HarEntryResponse], HarEntryResponse]:
    if name not in _RESPONSE_REWRITE_RULES:
        raise ResponseRuleNotFoundException(name)
    return _RESPONSE_REWRITE_RULES[name]


def _apply_request_rules(config: Config, request: HarEntryRequest, index: int) -> HarEntryRequest:
    rules = config.rewrite_rules.request_rules
    if len(rules) == 0:
        return request

    request_copy = copy.deepcopy(request)
    for rule in rules:
        request_copy = _get_request_rewrite_rule(rule)[index](config, request_copy)
    return request_copy


def apply_browser_request_rules(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _apply_request_rules(config, request, 0)


def apply_entry_request_rules(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    return _apply_request_rules(config, request, 1)


def apply_response_rules(config: Config, response: HarEntryResponse) -> HarEntryResponse:
    rules = config.rewrite_rules.response_rules
    if len(rules) == 0:
        return response

    response_copy = copy.deepcopy(response)
    for rule in rules:
        response_copy = _get_response_rewrite_rule(rule)(config, response_copy)
    return response_copy
