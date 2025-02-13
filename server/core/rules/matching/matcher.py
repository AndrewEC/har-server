from typing import Annotated
from functools import lru_cache
import logging

from fastapi import Depends

from server.core.config import ConfigLoader, with_config_loader
from server.core.config.models import Matchers
from server.core.har import HarEntryRequest
from server.core.rules.base import RuleContainer, RuleFailedException

from .rules import (
    MethodMatcherRule,
    PathMatcherRule,
    QueryMatcherRule,
    HeadersMatcherRule,
    CookieMatcherRule,
    MatcherRule,
    BodyMatcherRule
)


_log = logging.getLogger(__file__)


class RequestMatcher:

    _MATCHERS = [
        MethodMatcherRule,
        PathMatcherRule,
        QueryMatcherRule,
        HeadersMatcherRule,
        CookieMatcherRule,
        BodyMatcherRule
    ]

    def __init__(self, config_loader: ConfigLoader):
        self._rule_container = RuleContainer[MatcherRule]('request-matcher', RequestMatcher._MATCHERS)

        rules = config_loader.read_config(Matchers).rules
        _log.info(f'Configured request matching rules: [{rules}]')
        self._rule_container.enable_rules(config_loader, rules)

    def do_requests_match(self, entry: HarEntryRequest, request: HarEntryRequest) -> bool:
        """
        This attempts to apply the configured matchers to test the har entry request against the incoming Http request
        to determine if the incoming Http request matches the har entry request.

        :param entry: The request pulled from a har file to be tested against the incoming Http request.
        :param request: The incoming Http request to be tested against the entry request.
        :return: True if the incoming Http request matching the har entry request. Otherwise, false.
        :raise MatchRuleNotFound: if any of the configured match rules could not be found.
        :raise MatchRuleFailedException: if any of the matchers raised an exception.
        """

        for name, rule in self._rule_container.get_enabled_rules().items():
            try:
                if not rule.matches(entry, request):
                    return False
            except Exception as e:
                raise RuleFailedException(self._rule_container.get_name(), name, e) from e
        return True


@lru_cache()
def with_request_matcher(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> RequestMatcher:
    return RequestMatcher(config_loader)
