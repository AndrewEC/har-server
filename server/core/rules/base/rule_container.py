from typing import Generic, TypeVar, Type, List, Dict

from server.core.config import ConfigLoader

from .error import (DuplicateRuleException, RuleNotFoundException,
                    RuleInitializationFailedException, ContainerRulesAlreadyEnabledException)
from .rule_dict import RuleDict
from .rule import Rule


_T = TypeVar('_T', bound=Rule)


class RuleContainer(Generic[_T]):

    def __init__(self, container_name: str, rules: List[Type[_T]]):
        self._container_name = container_name
        self._rules = RuleDict()
        self._enabled_rules: List[str] = []
        for rule in rules:
            self._register_rule(rule)

    def get_name(self):
        return self._container_name

    def enable_rules(self, config_loader: ConfigLoader, names: List[str]):
        """
        Enables one or more of the registered rules. When a rule is being enabled
        the config_loader will be used to give the rule a chance to initialize and load
        any required configuration values.

        This method should only be called once. If this method was previously invoked,
        and at least one rule was successfully enabled, this will raise
        ContainerRulesAlreadyEnabled.

        :param config_loader: The config loader that will be passed to each of the rules
            being enabled so each rule has a chance to load any required configuration
            values.
        :param names: The names of the rules to be enabled.
        :raises ContainerRulesAlreadyEnabledException: Raised if this method has already
            been invoked and at least one rule has been enabled.
        :raises RuleNotFoundException: Raised if any of the input names specified does
            not map to a known rule.
        :raises RuleInitializationFailedException: Raised if any of the rules raises
            an exception when attempting to initialize.
        """
        if self.has_any_rules_enabled():
            raise ContainerRulesAlreadyEnabledException(self._container_name)
        for name in names:
            self._initialize_rule(config_loader, name)

    def _get_rule(self, name: str) -> _T:
        if name not in self._rules:
            raise RuleNotFoundException(self._container_name, name)
        return self._rules[name]

    def get_enabled_rules(self) -> Dict[str, _T]:
        """
        Gets a dict of the currently enabled rules and all their names.

        :return: A dictionary containing a mapping of the rules (values) and their
            respective names (keys).
        """
        return {name: self._get_rule(name) for name in self._enabled_rules}

    def _register_rule(self, rule: Type[_T]):
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
            raise RuleInitializationFailedException(self._container_name, name, e) from e
        self._enabled_rules.append(name)

    def has_any_rules_enabled(self) -> bool:
        """
        Indicates if this contain has at least one rule that has been successfully enabled.

        :return: True if at least one rule is enabled. Otherwise, false.
        """
        return len(self._enabled_rules) > 0
