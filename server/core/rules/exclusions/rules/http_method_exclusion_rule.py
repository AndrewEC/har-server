from typing import List

from server.core.har import HarEntry
from server.core.config import ConfigLoader, get_prop_config_path
from server.core.config.models import ExclusionConfig
from server.core.rules.base import MissingConfigPropertyException

from .base import ExclusionRule


class HttpMethodExclusionRule(ExclusionRule):

    def __init__(self):
        self._removable_http_methods: List[str] = []

    def get_name(self) -> str:
        return 'requests-with-http-method'

    def initialize(self, config_loader: ConfigLoader):
        self._removable_http_methods = config_loader.read_config(ExclusionConfig).removable_http_methods
        if len(self._removable_http_methods) == 0:
            property_path = get_prop_config_path(ExclusionConfig, 'removable_http_methods')
            raise MissingConfigPropertyException(self.get_name(), property_path)

    def should_filter_out(self, entry: HarEntry) -> bool:
        return entry.request.method in self._removable_http_methods
