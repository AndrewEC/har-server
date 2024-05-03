from typing import Annotated, Dict, Callable
from functools import lru_cache
import copy
import logging

from fastapi import Depends

from server.core.config import ConfigLoader, with_config_loader
from server.core.config.models import ResponseRewriteRules
from server.core.har import HarEntryResponse

from .errors import ResponseRuleNotFoundException, ResponseRuleFailedException
from .rules import remove_headers_from_response, remove_cookies_from_response, rewrite_response_content_urls


_log = logging.getLogger(__file__)


class ResponseRewriter:

    _RESPONSE_REWRITE_RULES: Dict[str, Callable[[ConfigLoader, HarEntryResponse], HarEntryResponse]] = {
        'urls-in-response': rewrite_response_content_urls,
        'remove-headers': remove_headers_from_response,
        'remove-cookies': remove_cookies_from_response
    }

    def __init__(self, config_loader: ConfigLoader):
        self._config_loader = config_loader
        self._rewrite_rules = self._config_loader.read_config(ResponseRewriteRules).rules
        _log.info(f'Configured response rewrite rules: [{self._rewrite_rules}]')

    def _get_response_rewrite_rule(self, name: str) -> Callable[[ConfigLoader, HarEntryResponse], HarEntryResponse]:
        if name not in ResponseRewriter._RESPONSE_REWRITE_RULES:
            raise ResponseRuleNotFoundException(name)
        return ResponseRewriter._RESPONSE_REWRITE_RULES[name]

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
        if len(self._rewrite_rules) == 0:
            return response

        response_copy = copy.deepcopy(response)
        for rule_name in self._rewrite_rules:
            rule_function = self._get_response_rewrite_rule(rule_name)
            try:
                response_copy = rule_function(self._config_loader, response_copy)
            except Exception as e:
                raise ResponseRuleFailedException(rule_name, e) from e
        return response_copy


@lru_cache()
def with_response_rewriter(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> ResponseRewriter:
    return ResponseRewriter(config_loader)
