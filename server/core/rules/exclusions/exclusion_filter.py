from typing import Annotated
from functools import lru_cache
import logging

from fastapi import Depends

from server.core.config import ConfigLoader, with_config_loader
from server.core.config.models import ExclusionRules
from server.core.har import HarEntry
from server.core.rules.base import RuleContainer, RuleFailedException

from .rules import ExclusionRule, BadStatusExclusionRule, InvalidSizeExclusionRule, HttpMethodExclusionRule


_log = logging.getLogger(__file__)


class ExclusionFilter(RuleContainer[ExclusionRule]):

    _EXCLUSION_RULES = [
        ('responses-with-status', BadStatusExclusionRule),
        ('responses-with-invalid-size', InvalidSizeExclusionRule),
        ('requests-with-http-method', HttpMethodExclusionRule)
    ]

    def __init__(self, config_loader: ConfigLoader):
        super().__init__('exclusion', ExclusionFilter._EXCLUSION_RULES)

        exclusion_rules = config_loader.read_config(ExclusionRules).rules
        _log.info(f'Configured exclusion rules: [{exclusion_rules}]')
        self.enable_rules(config_loader, exclusion_rules)

    def should_exclude_entry(self, entry: HarEntry) -> bool:
        """
        Iterates through, and applies all, exclusion filters to the entry to determine if the entry should be excluded.

        If this returns true then the input entry should be excluded and not be tested against an
        incoming request to determine if the request matches.

        This will return immediately as soon as the first exclusion rule determines the entry should be excluded.

        :param entry: The entry pulled from a har file to test against the exclusion filter rules.
        :return: True if the entry should be excluded, otherwise false.
        """
        if not self.has_any_rules_enabled():
            return False

        for name, rule in self.get_enabled_rules():
            try:
                if rule.should_filter_out(entry):
                    return True
            except Exception as e:
                raise RuleFailedException(self._container_name, name, e) from e
        return False


@lru_cache()
def with_exclusion_filter(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> ExclusionFilter:
    return ExclusionFilter(config_loader)
