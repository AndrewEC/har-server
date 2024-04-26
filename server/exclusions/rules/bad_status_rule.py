import logging

from server.har import HarEntry
from server.config import ConfigLoader
from server.config.models import RemovableStatuses


_log = logging.getLogger(__file__)


def bad_status_exclusion_rule(config: ConfigLoader, entry: HarEntry) -> bool:
    statuses = config.read_config(RemovableStatuses).removable_statuses
    if len(statuses) == 0:
        _log.warning('responses-with-status entry filter is enabled but no '
                     'entry-exclusion.config.removable-statuses status code array has been specified.')
        return False

    return entry.response.status in statuses
