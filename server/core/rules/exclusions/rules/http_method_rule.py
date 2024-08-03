import logging

from server.core.har import HarEntry
from server.core.config import ConfigLoader
from server.core.config.models import ExclusionConfig


_log = logging.getLogger(__file__)


def http_method_exclusion_rule(config: ConfigLoader, entry: HarEntry) -> bool:
    removable_http_methods = config.read_config(ExclusionConfig).removable_http_methods
    if len(removable_http_methods) == 0:
        _log.warning('http-method-exclusion entry filter is enabled but no '
                     'entry-exclusion.config.removable-http-methods array has been specified.')
        return False
    return entry.request.method in removable_http_methods
