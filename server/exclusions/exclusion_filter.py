from typing import Annotated, Dict, Callable
from functools import lru_cache
import logging

from fastapi import Depends

from server.config import ConfigLoader, with_config_loader
from server.config.models import ExclusionRules
from server.har import HarEntry

from .errors import EntryExclusionRuleNotFoundException, ExclusionRuleFailedException
from .rules import bad_status_exclusion_rule, invalid_size_exclusion_rule


_log = logging.getLogger(__file__)


class ExclusionFilter:

    _EXCLUSION_RULES: Dict[str, Callable[[ConfigLoader, HarEntry], bool]] = {
        'responses-with-status': bad_status_exclusion_rule,
        'responses-with-invalid-size': invalid_size_exclusion_rule
    }

    def __init__(self, config_loader: ConfigLoader):
        self._config_loader = config_loader
        self._exclusion_rules = self._config_loader.read_config(ExclusionRules).rules
        _log.info(f'Configured exclusion rules: [{self._exclusion_rules}]')

    def _get_exclusion_rule(self, rule_name: str) -> Callable[[ConfigLoader, HarEntry], bool]:
        if rule_name not in ExclusionFilter._EXCLUSION_RULES:
            raise EntryExclusionRuleNotFoundException(rule_name)
        return ExclusionFilter._EXCLUSION_RULES[rule_name]

    def should_exclude_entry(self, entry: HarEntry) -> bool:
        """
        Iterates through, and applies all, exclusion filters to the entry to determine if the entry should be excluded.

        If this returns true then the input entry should be excluded and not be tested against an
        incoming request to determine if the request matches.

        This will return immediately as soon as the first exclusion rule determines the entry should be excluded.

        :param entry: The entry pulled from a har file to test against the exclusion filter rules.
        :return: True if the entry should be excluded, otherwise false.
        """
        if len(self._exclusion_rules) == 0:
            return False

        for rule in self._exclusion_rules:
            exclusion_rule_function = self._get_exclusion_rule(rule)
            try:
                if exclusion_rule_function(self._config_loader, entry):
                    return True
            except Exception as e:
                raise ExclusionRuleFailedException(rule, e)
        return False


@lru_cache()
def with_exclusion_filter(config_loader: Annotated[ConfigLoader, Depends(with_config_loader)]) -> ExclusionFilter:
    return ExclusionFilter(config_loader)
