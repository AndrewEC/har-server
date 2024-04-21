from typing import Callable, List, Dict
import logging

from server.parse import HarFileContent
from server.config import Config

from .bad_status_rule import bad_status_exclusion_rule
from .invalid_size_rule import invalid_size_exclusion_rule
from .duplicate_rule import remove_duplicates_exclusion_rule


_log = logging.getLogger(__file__)

_EXCLUSION_RULES: Dict[str, Callable[[Config, List[HarFileContent]], List[HarFileContent]]] = {
    'responses-with-bad-status': bad_status_exclusion_rule,
    'responses-with-invalid-size': invalid_size_exclusion_rule,
    'duplicate-requests': remove_duplicates_exclusion_rule
}


class EntryExclusionRuleNotFoundException(Exception):

    _MESSAGE_TEMPLATE = 'A filter with the name [{}] could not be found.'

    def __init__(self, name: str):
        super().__init__(EntryExclusionRuleNotFoundException._MESSAGE_TEMPLATE.format(name))


class ExclusionRuleFailedException(Exception):

    _MESSAGE_TEMPLATE = 'The exclusion rule [{}] failed with an error.'

    def __init__(self, name: str, cause: Exception):
        super().__init__(ExclusionRuleFailedException._MESSAGE_TEMPLATE.format(name), cause)


def _get_exclusion_rule(name: str) -> Callable[[Config, List[HarFileContent]], List[HarFileContent]]:
    if name not in _EXCLUSION_RULES:
        raise EntryExclusionRuleNotFoundException(name)
    return _EXCLUSION_RULES[name]


def _sort_hars_by_name(file_contents: List[HarFileContent]) -> List[HarFileContent]:
    return list(sorted(file_contents, key=lambda file_content: str(file_content.source_file).lower()))


def _remove_files_with_no_entries(file_contents: List[HarFileContent]) -> List[HarFileContent]:
    files_with_entries = []
    for file_content in file_contents:
        if len(file_content.entries) == 0:
            _log.info(f'.har file will be excluded because it does not have any remaining entries: [{file_content.source_file}]')
            continue
        files_with_entries.append(file_content)
    return files_with_entries


def apply_entry_exclusions(config: Config, file_contents: List[HarFileContent]) -> List[HarFileContent]:
    """
    Applies the configured exclusion rules to the har file contents to remove any entries in each har file
    that match at least one of the exclusion rules. This process will mutate the har file contents in place.

    This will also remove any har file content in the input file_contents list if there are no entries remaining in the
    har file content.

    :param config: The server configuration from which the list of exclusion rules will be pulled.
    :param file_contents: The list of parsed har file contents.
    :return: The list of parsed har file contents less any har files that no longer have any entries as a result of
        these exclusion rules.
    :raise: EntryExclusionRuleNotFoundException if an exclusion rule specified in the configuration could not be found.
    :raise: ExclusionRuleFailedException if an exclusion rule raised an exception. This exception will contain the
        original exception that was raised by the exclusion rule.
    """

    file_contents = _sort_hars_by_name(_remove_files_with_no_entries(file_contents))
    rules = config.exclusions.rules
    if len(rules) == 0:
        _log.info('No entry-exclusions.rules array has been configured. No har file entries will be filtered out.')
        return file_contents
    for rule in rules:
        _log.info(f'Applying entry exclusion rule: [{rule}]')
        exclusion_rule_function = _get_exclusion_rule(rule)
        try:
            entries_post_exclusion_rule = exclusion_rule_function(config, file_contents)
        except Exception as e:
            raise ExclusionRuleFailedException(rule, e)
        file_contents = _sort_hars_by_name(_remove_files_with_no_entries(entries_post_exclusion_rule))
    return file_contents
