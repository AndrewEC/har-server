from typing import Annotated
from functools import lru_cache
from enum import Enum
import copy
import logging

from fastapi import Depends

from server.core.config import with_config_loader, ConfigLoader
from server.core.config.models import RequestRewriteRules
from server.core.har import HarEntryRequest
from server.core.rules.base import RuleContainer, RuleFailedException

from .rules import (RemoveRequestHeaderRequestRewriteRule, RemoveQueryParamsRequestRewriteRule,
                    RemoveCookieRequestRewriteRule, RequestRewriteRule)


_log = logging.getLogger(__file__)


class ModificationType(Enum):
    REQUEST = 1
    ENTRY = 2


class RequestRewriter:

    _REQUEST_REWRITE_RULES = [
        RemoveQueryParamsRequestRewriteRule,
        RemoveRequestHeaderRequestRewriteRule,
        RemoveCookieRequestRewriteRule
    ]

    def __init__(self, config_loader: ConfigLoader):
        self._rule_container = RuleContainer[RequestRewriteRule](
            'request-rewrite',
            RequestRewriter._REQUEST_REWRITE_RULES
        )

        rewrite_rules = config_loader.read_config(RequestRewriteRules).rules
        _log.info(f'Configured request rewrite rules: [{rewrite_rules}]')
        self._rule_container.enable_rules(config_loader, rewrite_rules)

    def _apply_request_rewrite_rules(self, request: HarEntryRequest, modification_type: ModificationType)\
            -> HarEntryRequest:

        if not self._rule_container.has_any_rules_enabled():
            return request

        request_copy = copy.deepcopy(request)
        for name, rule in self._rule_container.get_enabled_rules().items():
            try:
                if modification_type == ModificationType.ENTRY:
                    request_copy = rule.rewrite_har_entry_request(request_copy)
                else:
                    request_copy = rule.rewrite_incoming_http_request(request_copy)
            except Exception as e:
                raise RuleFailedException(self._rule_container.get_name(), name, e) from e
        return request_copy

    def apply_browser_request_rewrite_rules(self, request: HarEntryRequest) -> HarEntryRequest:
        """
        Applies the request rewrite rule to mutate the incoming Http request argument.

        This will not mutate the input request parameter. Rather, this will make a deepcopy of the request object,
        pass the copy to the rewrite rules, then return the mutated copy.

        If no rewrite rules have been specified then this will return the input request without any modification
        or copying.

        :param request: The incoming Http request to be modified.
        :return: The mutated copy of the input request object.
        :raise RequestRuleNotFoundException: if one of the request rewrite rules configured could not be found.
        :raise RequestRuleFailedException: if any of the rewrite rules raised an exception.
        """
        return self._apply_request_rewrite_rules(request, ModificationType.REQUEST)

    def apply_entry_request_rewrite_rules(self, request: HarEntryRequest) -> HarEntryRequest:
        """
        Applies the request rewrite rule to mutate the request pulled from a har file.

        This will not mutate the input request parameter. Rather, this will make a deepcopy of the request object, pass
        the copy to the rewrite rules, then return the mutated copy.

        If no rewrite rules have been specified then this will return the input request without any modification
        of copying.

        :param request: The request pulled from a har file to be mutated.
        :return: The mutated copy of the input request object.
        :raise RequestRuleNotFoundException: if one of the request rewrite rules configured could not be found.
        :raise RequestRuleFailedException: if any of the rewrite rules raised an exception.
        """
        return self._apply_request_rewrite_rules(request, ModificationType.ENTRY)


@lru_cache()
def with_request_rewriter(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> RequestRewriter:
    return RequestRewriter(config_loader)
