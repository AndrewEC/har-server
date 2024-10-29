from abc import abstractmethod, ABC

from server.core.har import HarEntryRequest
from server.core.rules.base import Rule


class MatcherRule(Rule, ABC):

    @abstractmethod
    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        pass
