from typing import List

from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader, get_prop_config_path
from server.core.config.models import RequestRewriteConfig
from server.core.rules.base import MissingConfigPropertyException

from .base import RequestRewriteRule


class RemoveQueryParamsRequestRewriteRule(RequestRewriteRule):

    def __init__(self):
        self._removable: List[str] = []

    def get_name(self) -> str:
        return 'remove-query-params'

    def initialize(self, config_loader: ConfigLoader):
        self._removable = config_loader.read_config(RequestRewriteConfig).removable_query_params
        if len(self._removable) == 0:
            property_path = get_prop_config_path(RequestRewriteConfig, 'removable_query_params')
            raise MissingConfigPropertyException(self.get_name(), property_path)

    def rewrite_incoming_http_request(self, request: HarEntryRequest) -> HarEntryRequest:
        return self._remove_params(request)

    def rewrite_har_entry_request(self, request: HarEntryRequest) -> HarEntryRequest:
        return self._remove_params(request)

    def _remove_params(self, request: HarEntryRequest) -> HarEntryRequest:
        for param in self._removable:
            if param not in request.query_params:
                continue
            request.query_params.pop(param)
        return request
