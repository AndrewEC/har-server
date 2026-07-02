from server.core.har import HarEntry
from server.core.config import ConfigLoader

from .base import ExclusionRule


class InvalidSizeExclusionRule(ExclusionRule):

    _EMPTY_STATUSES = [
        204,
        301,
        302
    ]

    def get_name(self) -> str:
        return 'responses-with-invalid-size'

    def initialize(self, config_loader: ConfigLoader):
        pass

    def should_filter_out(self, entry: HarEntry) -> bool:
        size = len(entry.response.content.text)
        return (
            size > 0 and entry.response.status in self._EMPTY_STATUSES
            or size == 0 and entry.response.status not in self._EMPTY_STATUSES
        )
