from typing import List

from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader
from server.core.rules.base import MissingConfigPropertyException

from .base import RequestRewriteRule


class RemoveRequestHeaderRequestRewriteRule(RequestRewriteRule):

    def __init__(self):
        self._removable_headers: List[str] = []

    def get_name(self) -> str:
        return 'remove-headers'

    def initialize(self, config_loader: ConfigLoader):
        self._removable_headers = config_loader.get_app_config().rewrite.request.config.removable_headers
        if len(self._removable_headers) == 0:
            raise MissingConfigPropertyException(self.get_name(), 'removable_headers')

    def rewrite_incoming_http_request(self, request: HarEntryRequest) -> HarEntryRequest:
        return self._remove_header_from_request(request)

    def rewrite_har_entry_request(self, request: HarEntryRequest) -> HarEntryRequest:
        return self._remove_header_from_request(request)

    def _remove_header_from_request(self, request: HarEntryRequest) -> HarEntryRequest:
        for removable in self._removable_headers:
            if removable not in request.headers:
                continue
            request.headers.pop(removable)
        return request
