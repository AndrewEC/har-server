from typing import Callable, Dict
import copy

from server.parse import HarEntryResponse
from server.config import Config

from .response import rewrite_response_content_urls, remove_headers_from_response
from .errors import ResponseRuleNotFoundException, ResponseRuleFailedException


_RESPONSE_REWRITE_RULES: Dict[str, Callable[[Config, HarEntryResponse], HarEntryResponse]] = {
    'urls-in-response': rewrite_response_content_urls,
    'remove-headers': remove_headers_from_response
}


def _get_response_rewrite_rule(name: str) -> Callable[[Config, HarEntryResponse], HarEntryResponse]:
    if name not in _RESPONSE_REWRITE_RULES:
        raise ResponseRuleNotFoundException(name)
    return _RESPONSE_REWRITE_RULES[name]


def apply_response_rewrite_rules(config: Config, response: HarEntryResponse) -> HarEntryResponse:
    """
    Applies the configured rules to rewrite the response before the response is sent back to the consuming client.

    This will not mutate the input har response. Rather, this will create a deepcopy of the response, pass the response
    to the rewrite rules, the return said response.

    If no response rewrite rules have been configured then this will return the original input response without
    modification of copying.

    :param config: The har-server configuration from which the configured response rewrite rules will be pulled.
    :param response: The response, pulled from a har file entry, to be modified then returned to the consuming client.
    :return: A modified copy of the input har response.
    :raise: ResponseRuleNotFoundException if any of the configured response rewrite rules could not be found
    :raise: ResponseRuleFailedException if any of the response rewrite rules raised an exception.
    """
    rules = config.rewrite_rules.response_rules
    if len(rules) == 0:
        return response

    response_copy = copy.deepcopy(response)
    for rule_name in rules:
        rule_function = _get_response_rewrite_rule(rule_name)
        try:
            response_copy = rule_function(config, response_copy)
        except Exception as e:
            raise ResponseRuleFailedException(rule_name, e)
    return response_copy
