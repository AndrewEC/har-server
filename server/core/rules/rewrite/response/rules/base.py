from abc import ABC, abstractmethod

from server.core.rules.base import Rule
from server.core.har import HarEntryResponse


class ResponseRewriteRule(Rule, ABC):

    @abstractmethod
    def rewrite_response(self, response: HarEntryResponse) -> HarEntryResponse:
        pass
