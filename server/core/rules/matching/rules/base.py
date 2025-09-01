from abc import abstractmethod, ABC
from typing import List

from server.core.har import HarEntryRequest, NameValuePair
from server.core.rules.base import Rule


class MatcherRule(Rule, ABC):

    @abstractmethod
    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        pass


def do_name_value_pairs_match(first: List[NameValuePair], second: List[NameValuePair]) -> bool:
    if len(first) != len(second):
        return False

    for i in range(len(first)):
        first_pair = first[i]
        if not _contains_match(first_pair, second):
            return False

    return True


def _contains_match(first: NameValuePair, second: List[NameValuePair]) -> bool:
    for i in range(len(second)):
        second_pair = second[i]
        if first.name == second_pair.name and first.value == second_pair.value:
            return True
    return False
