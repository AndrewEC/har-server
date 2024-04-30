from typing import Annotated, Dict, Callable, List
from functools import lru_cache
import logging

from fastapi import Depends

from server.core.config import ConfigLoader, with_config_loader
from server.core.config.models import Matchers
from server.core.har import HarEntryRequest

from .matchers import (do_paths_match, do_cookies_match, do_queries_match, do_headers_match, do_methods_match,
                       MatchRuleFailedException, MatchRuleNotFound)


_log = logging.getLogger(__file__)


class RequestMatcher:

    _MATCHERS: Dict[str, Callable[[ConfigLoader, HarEntryRequest, HarEntryRequest], bool]] = {
        'method': do_methods_match,
        'path': do_paths_match,
        'query-params': do_queries_match,
        'headers': do_headers_match,
        'cookies': do_cookies_match
    }

    def __init__(self, config_loader: ConfigLoader):
        self._config_loader = config_loader
        self._applicable_rules = self._get_applicable_rules()
        _log.info(f'Configured request matching rules: [{self._applicable_rules}]')

    def _get_applicable_rules(self) -> List[str]:
        rules = self._config_loader.read_config(Matchers).rules
        if len(rules) > 0:
            return rules
        _log.info('No request matching rules have been configured. All available matching rules will be used '
                  'in default order.')
        return list(RequestMatcher._MATCHERS.keys())

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

        # Assumption here is that there will always be at least one rule specified.
        for rule_name in self._applicable_rules:
            matcher_function = self._get_rule(rule_name)
            try:
                if not matcher_function(self._config_loader, entry, request):
                    return False
            except Exception as e:
                raise MatchRuleFailedException(rule_name, e)
        return True

    def _get_rule(self, name: str) -> Callable[[ConfigLoader, HarEntryRequest, HarEntryRequest], bool]:
        if name not in RequestMatcher._MATCHERS:
            raise MatchRuleNotFound(name)
        return RequestMatcher._MATCHERS[name]


@lru_cache()
def with_request_matcher(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> RequestMatcher:
    return RequestMatcher(config_loader)
