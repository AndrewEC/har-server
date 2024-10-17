from typing import Generic, TypeVar, Type, List, Tuple
from abc import ABC

from server.core.config import ConfigLoader

from .error import DuplicateRuleException, RuleNotFoundException, RuleInitializationFailed, ContainerRulesAlreadyEnabled
from .initializable import Initializeable


T = TypeVar('T', bound=Initializeable)


class LowerKeyDict:

    def __init__(self):
        self._entries = dict()

    def _verify_key(self, item):
        if type(item) is not str:
            raise ValueError('LowerKeyDict only supports string keys.')

    def __contains__(self, item):
        self._verify_key(item)
        return item.lower() in self._entries

    def __getitem__(self, item):
        self._verify_key(item)
        return self._entries[item.lower()]

    def __setitem__(self, key, value):
        self._verify_key(key)
        self._entries[key.lower()] = value


class RuleContainer(Generic[T], ABC):

    def __init__(self, container_name: str, rules: List[Tuple[str, Type[T]]]):
        self._container_name = container_name
        self._rules = LowerKeyDict()
        self._enabled_rules: List[str] = []
        for rule in rules:
            self._register_rule(rule[0], rule[1])

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

    def _register_rule(self, name: str, rule: Type[T]):
        if name in self._rules:
            raise DuplicateRuleException(self._container_name, name)
        self._rules[name] = rule()

    def _initialize_rule(self, config_loader: ConfigLoader, name: str):
        rule = self._get_rule(name)
        try:
            rule.load_config(config_loader)
        except Exception as e:
            raise RuleInitializationFailed(self._container_name, name, e) from e
        self._enabled_rules.append(name)

    def has_any_rules_enabled(self) -> bool:
        return len(self._enabled_rules) > 0
