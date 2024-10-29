from typing import Generic, TypeVar, Type, List, Tuple
from abc import ABC

from server.core.config import ConfigLoader

from .error import (DuplicateRuleException, RuleNotFoundException,
                    RuleInitializationFailed, ContainerRulesAlreadyEnabled)
from .rule_dictionary import RuleDict
from .rule import Rule


T = TypeVar('T', bound=Rule)


class RuleContainer(Generic[T], ABC):

    def __init__(self, container_name: str, rules: List[Type[T]]):
        self._container_name = container_name
        self._rules = RuleDict()
        self._enabled_rules: List[str] = []
        for rule in rules:
            self._register_rule(rule)

    def enable_rules(self, config_loader: ConfigLoader, names: List[str]):
        if len(self._enabled_rules) > 0:
            raise ContainerRulesAlreadyEnabled(self._container_name)
        for name in names:
            self._initialize_rule(config_loader, name)

    def _get_rule(self, name: str) -> T:
        if name not in self._rules:
            raise RuleNotFoundException(self._container_name, name)
        return self._rules[name]

    def get_enabled_rules(self) -> List[Tuple[str, T]]:
        return [(name, self._get_rule(name)) for name in self._enabled_rules]

    def _register_rule(self, rule: Type[T]):
        rule_instance = rule()
        name = rule_instance.get_name()
        if name in self._rules:
            raise DuplicateRuleException(self._container_name, name)
        self._rules[name] = rule_instance

    def _initialize_rule(self, config_loader: ConfigLoader, name: str):
        rule = self._get_rule(name)
        try:
            rule.initialize(config_loader)
        except Exception as e:
            raise RuleInitializationFailed(self._container_name, name, e) from e
        self._enabled_rules.append(name)

    def has_any_rules_enabled(self) -> bool:
        return len(self._enabled_rules) > 0
