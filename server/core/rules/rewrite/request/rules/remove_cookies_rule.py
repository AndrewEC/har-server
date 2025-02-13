import logging

from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader, get_prop_config_path
from server.core.config.models import RequestRewriteConfig
from server.core.rules.base import MissingConfigPropertyException

from .base import RequestRewriteRule


_log = logging.getLogger(__file__)


class RemoveCookieRequestRewriteRule(RequestRewriteRule):

    def __init__(self):
        self._removable = []

    def get_name(self) -> str:
        return 'remove-cookies'

    def initialize(self, config_loader: ConfigLoader):
        self._removable = config_loader.read_config(RequestRewriteConfig).removable_cookies
        if len(self._removable) == 0:
            prop_path = get_prop_config_path(RequestRewriteConfig, 'removable_cookies')
            raise MissingConfigPropertyException(self.get_name(), prop_path)

    def rewrite_incoming_http_request(self, request: HarEntryRequest) -> HarEntryRequest:
        return self._remove_cookies(request)

    def rewrite_har_entry_request(self, request: HarEntryRequest) -> HarEntryRequest:
        return self._remove_cookies(request)

    def _remove_cookies(self, request: HarEntryRequest) -> HarEntryRequest:
        for cookie in self._removable:
            if cookie not in request.cookies:
                continue
            request.cookies.pop(cookie)
        return request
