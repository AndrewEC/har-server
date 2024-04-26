from server.har import HarEntry
from server.config import ConfigLoader


def invalid_size_exclusion_rule(config: ConfigLoader, entry: HarEntry) -> bool:
    text = entry.response.content.text
    size = len(text) if text is not None else 0
    return not ((size > 0 and entry.response.status != 204) or (size == 0 and entry.response.status == 204))
