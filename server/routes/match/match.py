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


def do_requests_match(config: Config, entry: HarEntryRequest, request: HarEntryRequest) -> bool:
    rule_matchers = [_get_rule(name) for name in config.matching.rules]
    if all(matcher(config, entry, request) for matcher in rule_matchers):
        return True


def _get_rule(name: str) -> Callable[[Config, HarEntryRequest, HarEntryRequest], bool]:
    if name not in _MATCHERS:
        raise MatchRuleNotFound(name)
    return _MATCHERS[name]
