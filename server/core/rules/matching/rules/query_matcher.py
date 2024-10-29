from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest

from .common import do_dicts_contain_same_elements
from .base import MatcherRule


class QueryMatcherRule(MatcherRule):

    def get_name(self) -> str:
        return 'query-params'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        return do_dicts_contain_same_elements(entry.query_params, incoming_request.query_params)
