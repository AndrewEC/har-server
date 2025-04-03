import logging

from server.core.har import HarEntry
from server.core.config import ConfigLoader, get_prop_config_path
from server.core.config.models import ExclusionConfig
from server.core.rules.base import MissingConfigPropertyException

from .base import ExclusionRule


_log = logging.getLogger(__file__)


class BadStatusExclusionRule(ExclusionRule):

    def __init__(self):
        self._statuses = []

    def get_name(self) -> str:
        return 'responses-with-status'

    def initialize(self, config_loader: ConfigLoader):
        self._statuses = config_loader.read_config(ExclusionConfig).removable_statuses
        if len(self._statuses) == 0:
            property_path = get_prop_config_path(ExclusionConfig, 'removable_statuses')
            raise MissingConfigPropertyException(self.get_name(), property_path)

    def should_filter_out(self, entry: HarEntry) -> bool:
        return entry.response.status in self._statuses
