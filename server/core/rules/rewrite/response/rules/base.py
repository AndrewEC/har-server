from abc import ABC, abstractmethod

from server.core.rules.base import Initializeable
from server.core.har import HarEntryResponse


class ResponseRewriteRule(Initializeable, ABC):

    @abstractmethod
    def rewrite_response(self, response: HarEntryResponse) -> HarEntryResponse:
        pass
