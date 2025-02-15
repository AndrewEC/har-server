import logging

from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest

from .base import MatcherRule


_log = logging.getLogger(__file__)


class HeadersMatcherRule(MatcherRule):

    def get_name(self) -> str:
        return 'headers'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        _log.debug(f'Comparing entry headers [{entry.headers}] to incoming header [{incoming_request.headers}].')
        return entry.headers == incoming_request.headers
