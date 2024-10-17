from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest

from .base import MatcherRule
from .common import do_dicts_contain_same_elements


class HeadersMatcherRule(MatcherRule):

    def load_config(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        return do_dicts_contain_same_elements(entry.headers, incoming_request.headers)
