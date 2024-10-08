import logging

from server.core.har import HarEntry
from server.core.config import ConfigLoader
from server.core.config.models import ExclusionConfig


_log = logging.getLogger(__file__)


def bad_status_exclusion_rule(config: ConfigLoader, entry: HarEntry) -> bool:
    statuses = config.read_config(ExclusionConfig).removable_statuses
    if len(statuses) == 0:
        _log.warning('responses-with-status entry filter is enabled but no '
                     'entry-exclusion.config.removable-statuses status code array has been specified.')
        return False

    return entry.response.status in statuses
