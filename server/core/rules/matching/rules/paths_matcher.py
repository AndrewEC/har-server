import logging

from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest

from .base import MatcherRule


_log = logging.getLogger(__file__)


class PathMatcherRule(MatcherRule):

    def get_name(self) -> str:
        return 'path'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        _log.debug(f'Comparing entry paths [{entry.path}] to incoming path [{incoming_request.path}].')
        return entry.path == incoming_request.path
