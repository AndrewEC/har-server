from typing import List

from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader
from server.core.rules.base import MissingConfigPropertyException

from .base import RequestRewriteRule


class RemoveCookieRequestRewriteRule(RequestRewriteRule):

    def __init__(self):
        self._removable: List[str] = []

    def get_name(self) -> str:
        return 'remove-cookies'

    def initialize(self, config_loader: ConfigLoader):
        self._removable = config_loader.get_app_config().rewrite.request.config.removable_cookies
        if len(self._removable) == 0:
            raise MissingConfigPropertyException(self.get_name(), 'removable_cookies')

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
