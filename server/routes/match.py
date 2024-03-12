from typing import Dict, Any, Callable

from server.parse import HarEntryRequest
from server.config import Config


class MatchRuleNotFound(Exception):

    _MESSAGE_TEMPLATE = 'Could not find request matcher named [{}].'

    def __init__(self, name: str):
        super().__init__(MatchRuleNotFound._MESSAGE_TEMPLATE.format(name))


def do_requests_match(config: Config, entry: HarEntryRequest, request: HarEntryRequest) -> bool:
    rule_matchers = [_get_rule(name) for name in config.matching.rules]
    if all(matcher(entry, request) for matcher in rule_matchers):
        return True


def _get_rule(name: str) -> Callable[[HarEntryRequest, HarEntryRequest], bool]:
    if name not in _MATCHERS:
        raise MatchRuleNotFound(name)
    return _MATCHERS[name]


def _do_headers_match(entry: HarEntryRequest, request: HarEntryRequest) -> bool:
    return _do_dictionaries_match(entry.headers, request.headers)


def _do_query_params_match(entry: HarEntryRequest, request: HarEntryRequest) -> bool:
    return _do_dictionaries_match(entry.query_params, request.query_params)


def _do_dictionaries_match(first: Dict[str, Any], second: Dict[str, Any]):
    if len(first) != len(second):
        return False
    for key in first.keys():
        if key not in second or first[key] != second[key]:
            return False
    return True


def _do_methods_match(entry: HarEntryRequest, request: HarEntryRequest) -> bool:
    return request.method == entry.method


def _do_paths_match(entry: HarEntryRequest, request: HarEntryRequest) -> bool:
    return request.path == entry.path


_MATCHERS: Dict[str, Callable[[HarEntryRequest, HarEntryRequest], bool]] = {
    'method': _do_methods_match,
    'path': _do_paths_match,
    'query-params': _do_query_params_match,
    'headers': _do_headers_match
}
