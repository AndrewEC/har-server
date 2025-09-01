import logging

from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader

from .base import MatcherRule, do_name_value_pairs_match


_log = logging.getLogger(__file__)


class CookieMatcherRule(MatcherRule):

    def get_name(self) -> str:
        return 'cookies'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        _log.debug(f'Comparing entry cookies [{entry.cookies}] to incoming cookies [{incoming_request.cookies}].')
        return do_name_value_pairs_match(entry.cookies, incoming_request.cookies)
