from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest

from .base import MatcherRule


class PathMatcherRule(MatcherRule):

    def load_config(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        return entry.path == incoming_request.path
