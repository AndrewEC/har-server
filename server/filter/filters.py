from typing import Callable, List, Dict
import logging

from server.parse import HarFileContent
from server.config import Config

from .bad_status import bad_status_filter
from .invalid_size import invalid_size_filter
from .duplicate import remove_duplicates


_log = logging.getLogger(__file__)

_FILTERS: Dict[str, Callable[[Config, List[HarFileContent]], List[HarFileContent]]] = {
    'responses-with-bad-status': bad_status_filter,
    'responses-with-invalid-size': invalid_size_filter,
    'duplicate-requests': remove_duplicates
}


class FilterNotFoundException(Exception):

    _MESSAGE_TEMPLATE = 'A filter with the name [{}] could not be found.'

    def __init__(self, name: str):
        super().__init__(FilterNotFoundException._MESSAGE_TEMPLATE.format(name))


def _get_exclusion_rule(name: str) -> Callable[[Config, List[HarFileContent]], List[HarFileContent]]:
    if name not in _FILTERS:
        raise FilterNotFoundException(name)
    return _FILTERS[name]


def _sort(file_contents: List[HarFileContent]) -> List[HarFileContent]:
    return list(sorted(file_contents, key=lambda file_content: str(file_content.source_file).lower()))


def apply_entry_filters(config: Config, file_contents: List[HarFileContent]) -> List[HarFileContent]:
    rules = config.exclusions.rules
    if len(rules) == 0:
        return file_contents
    for rule in rules:
        _log.info(f'Applying entry filter: [{rule}]')
        file_contents = _sort(_get_exclusion_rule(rule)(config, file_contents))
    return file_contents
