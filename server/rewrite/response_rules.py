from typing import Callable, Dict
import copy

from server.parse import HarEntryResponse
from server.config import Config

from .response import rewrite_response_content_urls, remove_headers_from_response
from .errors import ResponseRuleNotFoundException


_RESPONSE_REWRITE_RULES: Dict[str, Callable[[Config, HarEntryResponse], HarEntryResponse]] = {
    'localhost': rewrite_response_content_urls,
    'remove-headers': remove_headers_from_response
}


def _get_response_rewrite_rule(name: str) -> Callable[[Config, HarEntryResponse], HarEntryResponse]:
    if name not in _RESPONSE_REWRITE_RULES:
        raise ResponseRuleNotFoundException(name)
    return _RESPONSE_REWRITE_RULES[name]


def apply_response_rewrite_rules(config: Config, response: HarEntryResponse) -> HarEntryResponse:
    rules = config.rewrite_rules.response_rules
    if len(rules) == 0:
        return response

    response_copy = copy.deepcopy(response)
    for rule in rules:
        response_copy = _get_response_rewrite_rule(rule)(config, response_copy)
    return response_copy
