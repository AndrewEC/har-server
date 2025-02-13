import logging

from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader

from .base import MatcherRule


_log = logging.getLogger(__file__)


class MethodMatcherRule(MatcherRule):

    def get_name(self) -> str:
        return 'method'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        _log.debug(f'Comparing entry method [{entry.method}] to incoming method [{incoming_request.method}].')
        return entry.method == incoming_request.method
