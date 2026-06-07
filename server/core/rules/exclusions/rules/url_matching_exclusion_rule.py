from typing import List, Any
import re
from re import Pattern

from server.core.har import HarEntry
from server.core.config import ConfigLoader
from server.core.rules.base import MissingConfigPropertyException

from .base import ExclusionRule


class UrlMatchingExclusionRule(ExclusionRule):

    def __init__(self):
        self._url_expressions: List[Pattern[Any]] = []

    def get_name(self) -> str:
        return 'requests-with-matching-url'
    
    def initialize(self, config_loader: ConfigLoader):
        expressions = config_loader.get_app_config().exclusions.config.removable_url_expressions
        if len(expressions) == 0:
            raise MissingConfigPropertyException(self.get_name(), 'removable_url_expressions')
        self._url_expressions = [re.compile(expression) for expression in expressions]

    def should_filter_out(self, entry: HarEntry) -> bool:
        return any(expression.match(entry.request.url) for expression in self._url_expressions)
