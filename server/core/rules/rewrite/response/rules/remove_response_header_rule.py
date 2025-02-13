import logging

from server.core.har import HarEntryResponse
from server.core.config import ConfigLoader, get_prop_config_path
from server.core.config.models import ResponseRuleConfig
from server.core.rules.base import MissingConfigPropertyException

from .base import ResponseRewriteRule

_log = logging.getLogger(__file__)


class RemoveResponseHeaderRewriteRule(ResponseRewriteRule):

    def __init__(self):
        self._removable = []

    def get_name(self) -> str:
        return 'remove-headers'

    def initialize(self, config_loader: ConfigLoader):
        self._removable = config_loader.read_config(ResponseRuleConfig).removable_headers
        if len(self._removable) == 0:
            property_path = get_prop_config_path(ResponseRuleConfig, 'removable_headers')
            raise MissingConfigPropertyException(self.get_name(), property_path)

    def rewrite_response(self, response: HarEntryResponse) -> HarEntryResponse:
        for removable in self._removable:
            if removable not in response.headers:
                continue
            response.headers.pop(removable)
        return response
