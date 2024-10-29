from typing import Annotated
from functools import lru_cache
import copy
import logging

from fastapi import Depends

from server.core.config import ConfigLoader, with_config_loader
from server.core.config.models import ResponseRewriteRules
from server.core.har import HarEntryResponse
from server.core.rules.base import RuleContainer, RuleFailedException

from .rules import (ResponseContentUrlResponseRewriteRules, RemoveResponseHeaderRewriteRule,
                    RemoveCookiesResponseRewriteRule, ResponseRewriteRule)


_log = logging.getLogger(__file__)


class ResponseRewriter(RuleContainer[ResponseRewriteRule]):

    _RESPONSE_REWRITE_RULES = [
        ResponseContentUrlResponseRewriteRules,
        RemoveResponseHeaderRewriteRule,
        RemoveCookiesResponseRewriteRule
    ]

    def __init__(self, config_loader: ConfigLoader):
        super().__init__('response-rewrite', ResponseRewriter._RESPONSE_REWRITE_RULES)
        rules = config_loader.read_config(ResponseRewriteRules).rules
        _log.info(f'Configured response rewrite rules: [{rules}]')
        self.enable_rules(config_loader, rules)

    def apply_response_rewrite_rules(self, response: HarEntryResponse) -> HarEntryResponse:
        """
        Applies the configured rules to rewrite the response before the response is sent back to the consuming client.

        This will not mutate the input har response. Rather, this will create a deepcopy of the response, pass the
        response to the rewrite rules, the return said response.

        If no response rewrite rules have been configured then this will return the original input response without
        modification or copying.

        :param response: The response, pulled from a har file entry, to be modified then returned to the consuming
            client.
        :return: A modified copy of the input har response.
        :raise ResponseRuleNotFoundException: if any of the configured response rewrite rules could not be found
        :raise ResponseRuleFailedException: if any of the response rewrite rules raised an exception.
        """
        if not self.has_any_rules_enabled():
            return response

        response_copy = copy.deepcopy(response)
        for name, rule in self.get_enabled_rules():
            try:
                response_copy = rule.rewrite_response(response_copy)
            except Exception as e:
                raise RuleFailedException(self._container_name, name, e) from e
        return response_copy


@lru_cache()
def with_response_rewriter(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> ResponseRewriter:
    return ResponseRewriter(config_loader)
