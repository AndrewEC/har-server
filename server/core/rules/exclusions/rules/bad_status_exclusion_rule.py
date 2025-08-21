from typing import List

from server.core.har import HarEntry
from server.core.config import ConfigLoader
from server.core.rules.base import MissingConfigPropertyException

from .base import ExclusionRule


class BadStatusExclusionRule(ExclusionRule):

    def __init__(self):
        self._statuses: List[int] = []

    def get_name(self) -> str:
        return 'responses-with-status'

    def initialize(self, config_loader: ConfigLoader):
        self._statuses = config_loader.get_app_config().exclusions.config.removable_statuses
        if len(self._statuses) == 0:
            raise MissingConfigPropertyException(self.get_name(), 'removable_statuses')

    def should_filter_out(self, entry: HarEntry) -> bool:
        return entry.response.status in self._statuses
