from typing import List

from server.core.har import HarEntry
from server.core.config import ConfigLoader
from server.core.rules.base import MissingConfigPropertyException

from .base import ExclusionRule


class HttpMethodExclusionRule(ExclusionRule):

    def __init__(self):
        self._removable_http_methods: List[str] = []

    def get_name(self) -> str:
        return 'requests-with-http-method'

    def initialize(self, config_loader: ConfigLoader):
        self._removable_http_methods = config_loader.get_app_config().exclusions.config.removable_http_methods
        if len(self._removable_http_methods) == 0:
            raise MissingConfigPropertyException(self.get_name(), 'removable_http_methods')

    def should_filter_out(self, entry: HarEntry) -> bool:
        return entry.request.method in self._removable_http_methods
