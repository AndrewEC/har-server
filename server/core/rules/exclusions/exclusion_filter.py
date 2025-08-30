from typing import Annotated, List, Type
from functools import lru_cache
import logging

from fastapi import Depends

from server.core.config import ConfigLoader, with_config_loader
from server.core.har import HarEntry
from server.core.rules.base import RuleContainer, RuleFailedException

from .rules import (
    ExclusionRule,
    BadStatusExclusionRule,
    InvalidSizeExclusionRule,
    HttpMethodExclusionRule
)


_log = logging.getLogger(__file__)


class ExclusionFilter:

    _EXCLUSION_RULES: List[Type[ExclusionRule]] = [
        BadStatusExclusionRule,
        InvalidSizeExclusionRule,
        HttpMethodExclusionRule
    ]

    def __init__(self, config_loader: ConfigLoader):
        self._rule_container = RuleContainer[ExclusionRule]('exclusion', ExclusionFilter._EXCLUSION_RULES)

        exclusion_rules = config_loader.get_app_config().exclusions.rules
        _log.info(f'Configured exclusion rules: [{exclusion_rules}]')
        self._rule_container.enable_rules(config_loader, exclusion_rules)

    def should_exclude_entry(self, entry: HarEntry) -> bool:
        """
        Iterates through and applies all exclusion filters to the entry to determine if the entry
        should be excluded.

        If this returns true then the input entry should be excluded and not be tested against an
        incoming request to determine if the request matches.

        This will return immediately as soon as the first exclusion rule determines the entry
        should be excluded.

        :param entry: The entry pulled from a har file to test against the exclusion filter rules.
        :return: True if the entry should be excluded, otherwise false.
        """
        if not self._rule_container.has_any_rules_enabled():
            return False

        for name, rule in self._rule_container.get_enabled_rules():
            try:
                if rule.should_filter_out(entry):
                    return True
            except Exception as e:
                raise RuleFailedException(self._rule_container.get_name(), name, e) from e
        return False


@lru_cache()
def with_exclusion_filter(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> ExclusionFilter:
    return ExclusionFilter(config_loader)
