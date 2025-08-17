import logging

from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest
from .base import MatcherRule


_log = logging.getLogger(__file__)


class BodyMatcherRule(MatcherRule):

    def get_name(self) -> str:
        return 'body'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        _log.debug(f'Comparing entry body: [{entry.body}] to incoming body: [{incoming_request.body}]')
        if entry.body is None and incoming_request.body is None:
            return True
        if entry.body is not None and incoming_request.body is None \
                or entry.body is None and incoming_request.body is not None:
            return False
        return entry.body == incoming_request.body
