from typing import List

from server.parse import HarFileContent, HarEntry
from server.config import Config


def _has_valid_size(entry: HarEntry) -> bool:
    text = entry.response.content.text
    size = len(text) if text is not None else 0
    return size > 0 or (size == 0 and entry.response.status == 204)


def invalid_size_filter(config: Config, file_contents: List[HarFileContent]) -> List[HarFileContent]:
    for file_content in file_contents:
        file_content.entries = list(filter(_has_valid_size, file_content.entries))
    return file_contents
