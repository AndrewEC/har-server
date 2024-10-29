from abc import ABC, abstractmethod

from server.core.rules.base import Rule
from server.core.har import HarEntry


class ExclusionRule(Rule, ABC):

    @abstractmethod
    def should_filter_out(self, entry: HarEntry) -> bool:
        pass
