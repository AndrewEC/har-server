import logging

from server.core.har import HarEntry
from server.core.config import ConfigLoader
from server.core.config.models import ExclusionConfig

from .base import ExclusionRule


_log = logging.getLogger(__file__)


class HttpMethodExclusionRule(ExclusionRule):

    def __init__(self):
        self._removable_http_methods = []

    def get_name(self) -> str:
        return 'requests-with-http-method'

    def initialize(self, config_loader: ConfigLoader):
        self._removable_http_methods = config_loader.read_config(ExclusionConfig).removable_http_methods
        if len(self._removable_http_methods) == 0:
            raise Exception('http-method-exclusion entry filter is enabled but no '
                            'entry-exclusion.config.removable-http-methods array has been specified.')

    def should_filter_out(self, entry: HarEntry) -> bool:
        return entry.request.method in self._removable_http_methods
