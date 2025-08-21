from typing import List

from server.core.har import HarEntryResponse
from server.core.config import ConfigLoader
from server.core.rules.base import MissingConfigPropertyException

from .base import ResponseRewriteRule


class RemoveHeaderResponseRewriteRule(ResponseRewriteRule):

    def __init__(self):
        self._removable: List[str] = []

    def get_name(self) -> str:
        return 'remove-headers'

    def initialize(self, config_loader: ConfigLoader):
        self._removable = config_loader.get_app_config().rewrite.response.config.removable_headers
        if len(self._removable) == 0:
            raise MissingConfigPropertyException(self.get_name(), 'removable_headers')

    def rewrite_response(self, response: HarEntryResponse) -> HarEntryResponse:
        for removable in self._removable:
            if removable not in response.headers:
                continue
            response.headers.pop(removable)
        return response
