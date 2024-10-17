from typing import Annotated, List
from functools import lru_cache
import logging

from fastapi import Depends

from server.core.config import ConfigLoader, with_config_loader
from server.core.config.models import Matchers
from server.core.har import HarEntryRequest
from server.core.rules.base import RuleContainer, RuleFailedException

from .rules import (MethodMatcherRule, PathMatcherRule, QueryMatcherRule, HeadersMatcherRule, CookieMatcherRule,
                    MatcherRule)


_log = logging.getLogger(__file__)


class RequestMatcher(RuleContainer[MatcherRule]):

    _MATCHERS = [
        ('method', MethodMatcherRule),
        ('path', PathMatcherRule),
        ('query-params', QueryMatcherRule),
        ('headers', HeadersMatcherRule),
        ('cookies', CookieMatcherRule)
    ]

    def __init__(self, config_loader: ConfigLoader):
        super().__init__('request-matcher', RequestMatcher._MATCHERS)
        applicable_rules = self._get_applicable_rules(config_loader)
        _log.info(f'Configured request matching rules: [{applicable_rules}]')
        self.enable_rules(config_loader, applicable_rules)

    def _get_applicable_rules(self, config_loader: ConfigLoader) -> List[str]:
        rules = config_loader.read_config(Matchers).rules
        if len(rules) > 0:
            return rules
        _log.info('No request matching rules have been configured. All available matching rules will be used '
                  'in default order.')
        return list(matcher[0] for matcher in RequestMatcher._MATCHERS)

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

        for name, rule in self.get_enabled_rules():
            try:
                if not rule.matches(entry, request):
                    return False
            except Exception as e:
                raise RuleFailedException(self._container_name, name, e) from e
        return True


@lru_cache()
def with_request_matcher(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> RequestMatcher:
    return RequestMatcher(config_loader)
