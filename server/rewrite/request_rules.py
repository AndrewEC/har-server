from typing import Callable, Dict, Tuple
import copy

from server.parse import HarEntryRequest
from server.config import Config

from .request import (remove_query_param_from_request, remove_query_param_from_entry_request,
                      remove_header_from_request, remove_header_from_entry_request)
from .errors import RequestRuleNotFoundException, RequestRuleFailedException


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
    for rule_name in rules:
        rule_function = _get_request_rewrite_rule(rule_name)[index]
        try:
            request_copy = rule_function(config, request_copy)
        except Exception as e:
            raise RequestRuleFailedException(rule_name, e)
    return request_copy


def apply_browser_request_rewrite_rules(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    """
    Applies the request rewrite rule to mutate the incoming Http request argument.

    This will not mutate the input request parameter. Rather, this will make a deepcopy of the request object, pass
    the copy to the rewrite rules, then return the mutated copy.

    If no rewrite rules have been specified then this will return the input request without any modification or copying.

    :param config: The har server configuration from which the list of configured request rewrite rules will be pulled.
    :param request: The incoming Http request to be modified.
    :return: The mutated copy of the input request object.
    :raise: RequestRuleNotFoundException if one of the request rewrite rules configured could not be found.
    :raise: RequestRuleFailedException if any of the rewrite rules raised an exception.
    """
    return _apply_request_rewrite_rules(config, request, 0)


def apply_entry_request_rewrite_rules(config: Config, request: HarEntryRequest) -> HarEntryRequest:
    """
    Applies the request rewrite rule to mutate the request pulled from a har file.

    This will not mutate the input request parameter. Rather, this will make a deepcopy of the request object, pass
    the copy to the rewrite rules, then return the mutated copy.

    If no rewrite rules have been specified then this will return the input request without any modification of copying.

    :param config: The har server configuration from which the list of configured request rewrite rules will be pulled.
    :param request: The request pulled from a har file to be mutated.
    :return: The mutated copy of the input request object.
    :raise: RequestRuleNotFoundException if one of the request rewrite rules configured could not be found.
    :raise: RequestRuleFailedException if any of the rewrite rules raised an exception.
    """
    return _apply_request_rewrite_rules(config, request, 1)
