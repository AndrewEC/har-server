from server.core.har import HarEntry
from server.core.config import ConfigLoader

from .base import ExclusionRule


class InvalidSizeExclusionRule(ExclusionRule):

    def load_config(self, config_loader: ConfigLoader):
        pass

    def should_filter_out(self, entry: HarEntry) -> bool:
        text = entry.response.content.text
        size = len(text) if text is not None else 0
        return not ((size > 0 and entry.response.status != 204) or (size == 0 and entry.response.status == 204))
