import logging

from server.core.har import HarEntryRequest
from server.core.config import ConfigLoader
from server.core.config.models import RequestRewriteConfig

from .base import RequestRewriteRule


_log = logging.getLogger(__file__)


class RemoveQueryParamsRequestRewriteRule(RequestRewriteRule):

    def __init__(self):
        self._removable = []

    def load_config(self, config_loader: ConfigLoader):
        self._removable = config_loader.read_config(RequestRewriteConfig).removable_query_params
        if len(self._removable) == 0:
            raise Exception('The remove-query-params request rewrite rule is enabled but no '
                            'removable-query-params have been configured.')

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
