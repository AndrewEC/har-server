from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader

from .base import MatcherRule


class MethodMatcherRule(MatcherRule):

    def load_config(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        return entry.method == incoming_request.method
