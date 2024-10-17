import logging

from server.core.har import HarEntry
from server.core.config import ConfigLoader
from server.core.config.models import ExclusionConfig

from .base import ExclusionRule


_log = logging.getLogger(__file__)


class BadStatusExclusionRule(ExclusionRule):

    def __init__(self):
        self._statuses = []

    def load_config(self, config_loader: ConfigLoader):
        self._statuses = config_loader.read_config(ExclusionConfig).removable_statuses
        if len(self._statuses) == 0:
            raise Exception('responses-with-status entry filter is enabled but no '
                            'entry-exclusion.config.removable-statuses status code array has been specified.')

    def should_filter_out(self, entry: HarEntry) -> bool:
        return entry.response.status in self._statuses
