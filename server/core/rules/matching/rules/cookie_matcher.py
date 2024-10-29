from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader

from .base import MatcherRule
from .common import do_dicts_contain_same_elements


class CookieMatcherRule(MatcherRule):

    def get_name(self) -> str:
        return 'cookies'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        return do_dicts_contain_same_elements(entry.cookies, incoming_request.cookies)
