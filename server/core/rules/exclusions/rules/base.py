from abc import ABC, abstractmethod

from server.core.rules.base import Initializeable
from server.core.har import HarEntry


class ExclusionRule(Initializeable, ABC):

    @abstractmethod
    def should_filter_out(self, entry: HarEntry) -> bool:
        pass
