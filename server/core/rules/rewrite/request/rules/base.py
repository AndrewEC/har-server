from abc import ABC, abstractmethod

from server.core.rules.base import Rule
from server.core.har import HarEntryRequest


class RequestRewriteRule(Rule, ABC):

    @abstractmethod
    def rewrite_incoming_http_request(self, request: HarEntryRequest) -> HarEntryRequest:
        pass

    @abstractmethod
    def rewrite_har_entry_request(self, request: HarEntryRequest) -> HarEntryRequest:
        pass
