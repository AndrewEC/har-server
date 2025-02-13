import logging

from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest

from .base import MatcherRule


_log = logging.getLogger(__file__)


class QueryMatcherRule(MatcherRule):

    def get_name(self) -> str:
        return 'query-params'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        _log.debug(f'Comparing entry query [{entry.query_params}] to incoming query [{incoming_request.query_params}].')
        return entry.query_params == incoming_request.query_params
