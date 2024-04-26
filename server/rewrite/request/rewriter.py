from typing import Annotated, Dict, Tuple, Callable
from functools import lru_cache
import copy
import logging

from fastapi import Depends

from server.config import with_config_loader, ConfigLoader
from server.config.models import RequestRewriteRules
from server.har import HarEntryRequest

from .rules import (remove_query_param_from_entry_request, remove_query_param_from_request,
                    remove_header_from_request, remove_header_from_entry_request,
                    remove_cookie_from_request, remove_cookie_from_entry_request)
from .errors import RequestRuleNotFoundException, RequestRuleFailedException


_log = logging.getLogger(__file__)


class RequestRewriter:

    _INCOMING_REQUEST_INDEX = 0
    _ENTRY_REQUEST_INDEX = 1

    _REQUEST_REWRITE_RULES: Dict[str, Tuple[Callable[[ConfigLoader, HarEntryRequest], HarEntryRequest], Callable[[ConfigLoader, HarEntryRequest], HarEntryRequest]]] = {
        'remove-query-params': (remove_query_param_from_request, remove_query_param_from_entry_request),
        'remove-headers': (remove_header_from_request, remove_header_from_entry_request),
        'remove-cookies': (remove_cookie_from_request, remove_cookie_from_entry_request)
    }

    def __init__(self, config_loader: ConfigLoader):
        self._config_loader = config_loader
        self._rewrite_rules = self._config_loader.read_config(RequestRewriteRules).rules
        _log.info(f'Configured request rewrite rules: [{self._rewrite_rules}]')

    def _get_request_rewrite_rule(self, name: str) -> Tuple[Callable[[ConfigLoader, HarEntryRequest], HarEntryRequest], Callable[[ConfigLoader, HarEntryRequest], HarEntryRequest]]:
        if name not in RequestRewriter._REQUEST_REWRITE_RULES:
            raise RequestRuleNotFoundException(name)
        return RequestRewriter._REQUEST_REWRITE_RULES[name]

    def _apply_request_rewrite_rules(self, request: HarEntryRequest, index: int) -> HarEntryRequest:
        if len(self._rewrite_rules) == 0:
            return request

        request_copy = copy.deepcopy(request)
        for rule_name in self._rewrite_rules:
            rule_function = self._get_request_rewrite_rule(rule_name)[index]
            try:
                request_copy = rule_function(self._config_loader, request_copy)
            except Exception as e:
                raise RequestRuleFailedException(rule_name, e)
        return request_copy

    def apply_browser_request_rewrite_rules(self, request: HarEntryRequest) -> HarEntryRequest:
        """
        Applies the request rewrite rule to mutate the incoming Http request argument.

        This will not mutate the input request parameter. Rather, this will make a deepcopy of the request object, pass
        the copy to the rewrite rules, then return the mutated copy.

        If no rewrite rules have been specified then this will return the input request without any modification or copying.

        :param request: The incoming Http request to be modified.
        :return: The mutated copy of the input request object.
        :raise RequestRuleNotFoundException: if one of the request rewrite rules configured could not be found.
        :raise RequestRuleFailedException: if any of the rewrite rules raised an exception.
        """
        return self._apply_request_rewrite_rules(request, RequestRewriter._INCOMING_REQUEST_INDEX)

    def apply_entry_request_rewrite_rules(self, request: HarEntryRequest) -> HarEntryRequest:
        """
        Applies the request rewrite rule to mutate the request pulled from a har file.

        This will not mutate the input request parameter. Rather, this will make a deepcopy of the request object, pass
        the copy to the rewrite rules, then return the mutated copy.

        If no rewrite rules have been specified then this will return the input request without any modification of copying.

        :param request: The request pulled from a har file to be mutated.
        :return: The mutated copy of the input request object.
        :raise RequestRuleNotFoundException: if one of the request rewrite rules configured could not be found.
        :raise RequestRuleFailedException: if any of the rewrite rules raised an exception.
        """
        return self._apply_request_rewrite_rules(request, RequestRewriter._ENTRY_REQUEST_INDEX)


@lru_cache()
def with_request_rewriter(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> RequestRewriter:
    return RequestRewriter(config_loader)
