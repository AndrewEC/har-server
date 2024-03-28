from typing import Dict, Callable

from server.parse import HarEntryRequest
from server.config import Config

from .method_matcher import do_methods_match
from .paths_matcher import do_paths_match
from .query_matcher import do_queries_match
from .headers_matcher import do_headers_match


_MATCHERS: Dict[str, Callable[[Config, HarEntryRequest, HarEntryRequest], bool]] = {
    'method': do_methods_match,
    'path': do_paths_match,
    'query-params': do_queries_match,
    'headers': do_headers_match
}


class MatchRuleNotFound(Exception):

    _MESSAGE_TEMPLATE = 'Could not find request matcher named [{}].'

    def __init__(self, name: str):
        super().__init__(MatchRuleNotFound._MESSAGE_TEMPLATE.format(name))


class MatchRuleFailedException(Exception):

    _MESSAGE_TEMPLATE = 'The match rule [{}] failed with an error.'

    def __init__(self, name: str, cause: Exception):
        super().__init__(MatchRuleFailedException._MESSAGE_TEMPLATE.format(name), cause)


def do_requests_match(config: Config, entry: HarEntryRequest, request: HarEntryRequest) -> bool:
    """
    This attempts to apply the configured matchers to test the har entry request against the incoming Http request
    to determine if the incoming Http request matches the har entry request.

    :param config: The har-server configuration from which the list of configured matchers will be pulled.
    :param entry: The request pulled from a har file to be tested against the incoming Http request.
    :param request: The incoming Http request to be tested against the entry request.
    :return: True if the incoming Http request matching the har entry request. Otherwise, false.
    :raise: MatchRuleNotFound if any of the configured match rules could not be found.
    :raise: MatchRuleFailedException if any of the matchers raised an exception.
    """

    # Assumption here is that there will always be at least one rule specified.
    for rule_name in config.matching.rules:
        matcher_function = _get_rule(rule_name)
        try:
            if not matcher_function(config, entry, request):
                return False
        except Exception as e:
            raise MatchRuleFailedException(rule_name, e)
    return True


def _get_rule(name: str) -> Callable[[Config, HarEntryRequest, HarEntryRequest], bool]:
    if name not in _MATCHERS:
        raise MatchRuleNotFound(name)
    return _MATCHERS[name]
