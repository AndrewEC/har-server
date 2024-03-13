from typing import Callable, List, Dict
import logging

from server.parse import HarFileContent
from server.config import Config

from .bad_status_filter import bad_status_filter
from .invalid_size_filter import invalid_size_filter
from .duplicate_filter import remove_duplicates


_log = logging.getLogger(__file__)

_EXCLUSION_RULES: Dict[str, Callable[[Config, List[HarFileContent]], List[HarFileContent]]] = {
    'responses-with-bad-status': bad_status_filter,
    'responses-with-invalid-size': invalid_size_filter,
    'duplicate-requests': remove_duplicates
}


class EntryExclusionRuleNotFoundException(Exception):

    _MESSAGE_TEMPLATE = 'A filter with the name [{}] could not be found.'

    def __init__(self, name: str):
        super().__init__(EntryExclusionRuleNotFoundException._MESSAGE_TEMPLATE.format(name))


def _get_exclusion_rule(name: str) -> Callable[[Config, List[HarFileContent]], List[HarFileContent]]:
    if name not in _EXCLUSION_RULES:
        raise EntryExclusionRuleNotFoundException(name)
    return _EXCLUSION_RULES[name]


def _sort(file_contents: List[HarFileContent]) -> List[HarFileContent]:
    return list(sorted(file_contents, key=lambda file_content: str(file_content.source_file).lower()))


def _remove_files_with_no_entries(file_contents: List[HarFileContent]) -> List[HarFileContent]:
    files_with_entries = []
    for file_content in file_contents:
        if len(file_content.entries) == 0:
            _log.info(f'.har file will be excluded because it does not have any remaining entries: [{file_content.source_file}]')
            continue
        files_with_entries.append(file_content)
    return files_with_entries


def apply_entry_filters(config: Config, file_contents: List[HarFileContent]) -> List[HarFileContent]:
    file_contents = _sort(_remove_files_with_no_entries(file_contents))
    rules = config.exclusions.rules
    if len(rules) == 0:
        _log.info('No entry-exclusions.rules array has been configured. No har file entries will be filtered out.')
        return file_contents
    for rule in rules:
        _log.info(f'Applying entry filter: [{rule}]')
        file_contents = _sort(_remove_files_with_no_entries(_get_exclusion_rule(rule)(config, file_contents)))
    return file_contents
