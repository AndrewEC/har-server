import logging

from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader, get_prop_config_path
from server.core.config.models import RequestRewriteConfig
from server.core.rules.base import MissingConfigPropertyException

from .base import RequestRewriteRule


_log = logging.getLogger(__file__)


class RemoveRequestHeaderRequestRewriteRule(RequestRewriteRule):

    def __init__(self):
        self._removable_headers = []

    def get_name(self) -> str:
        return 'remove-headers'

    def initialize(self, config_loader: ConfigLoader):
        self._removable_headers = config_loader.read_config(RequestRewriteConfig).removable_headers
        if len(self._removable_headers) == 0:
            property_path = get_prop_config_path(RequestRewriteConfig, 'removable_headers')
            raise MissingConfigPropertyException(self.get_name(), property_path)

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
