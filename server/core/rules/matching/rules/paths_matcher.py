from typing import Dict, Any
import logging
import re

from server.core.config import ConfigLoader
from server.core.har import HarEntryRequest

from .base import MatcherRule


_log = logging.getLogger(__file__)


class PathMatcherRule(MatcherRule):

    _WILDCARD = '*'

    def get_name(self) -> str:
        return 'path'

    def initialize(self, config_loader: ConfigLoader):
        self._expressions: Dict[str, Any] = dict()

    def matches(self, entry: HarEntryRequest, incoming_request: HarEntryRequest) -> bool:
        _log.debug(f'Comparing entry paths [{entry.path}] to incoming path [{incoming_request.path}].')
        if PathMatcherRule._WILDCARD in entry.path:
            compiled = self._expressions.get(entry.path)
            if compiled is None:
                expression = '^' + entry.path.replace('*', '.*').replace('/', '\\/') + '$'
                _log.debug(f"Matching using expression [{expression}].")
                compiled = re.compile(expression)
                self._expressions[entry.path] = compiled
            return compiled.match(incoming_request.path) is not None
        else:
            return entry.path == incoming_request.path
