from typing import List
import logging

from server.parse import HarFileContent
from server.config import Config


_log = logging.getLogger(__file__)


def bad_status_filter(config: Config, file_contents: List[HarFileContent]) -> List[HarFileContent]:
    statuses = config.exclusions.exclusion_config.bad_statuses
    if len(statuses) == 0:
        _log.warning('bad-status entry filter is enabled but no '
                     'entry-exclusion.config.bad-statuses status code array has been specified.')
        return file_contents

    _log.info(f'Filtering out entries with response status of: [{statuses}]')
    for file_content in file_contents:
        file_content.entries = [entry for entry in file_content.entries if entry.response.status not in statuses]
    return file_contents
