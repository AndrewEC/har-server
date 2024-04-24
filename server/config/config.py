from typing import Dict, TypeVar, Callable
import logging
from pathlib import Path
import yaml

from .models import (Debug, Server, MatchConfig, Matching, ExclusionConfig, ConfiguredExclusions, RewriteRulesConfig,
                     ConfiguredRewriteRules)

_log = logging.getLogger(__file__)
T = TypeVar('T')


class ConfigException(Exception):

    def __init__(self, message: str, e: Exception):
        super().__init__(message, e)


class Config:

    """
    Global configuration class intended to parse and hold the configuration values from the default
    _config.yml configuration file.
    """

    def __init__(self):
        self.debug = Debug()
        self.server = Server()
        self.exclusions = ConfiguredExclusions()
        self.rewrite_rules = ConfiguredRewriteRules()
        self.matching = Matching()

    def load(self, root_path: Path):
        """
        Parses the _config.yml file from the har directory specified when running the har-server.

        If no _config.yml file can be found this will immediately return and the default configs will be used.

        :param root_path: The path to the directory containing the _config.yml file.
        :raise ConfigException: if an any error occurs while trying to parse the config file.
        """
        try:
            self._do_load(root_path)
        except Exception as e:
            raise ConfigException('Could not load configuration from _config.yml file.', e)

    def _do_load(self, root_path: Path):
        parsed = self._parse_config_yml(root_path)
        if parsed is None:
            return

        get_or_default = self._curry_get_or_default(parsed)

        self.debug = Debug(
            get_or_default('debug.log-stack-traces', False),
            get_or_default('debug.dump-urls', False),
            get_or_default('debug.enable-debug-logs', False)
        )

        self.server = Server(
            get_or_default('server.port', 8080),
            get_or_default('server.open', None)
        )

        self.matching = Matching(
            get_or_default('request-matching.rules', []),
            MatchConfig()
        )

        self.exclusions = ConfiguredExclusions(
            get_or_default('entry-exclusions.rules', []),
            ExclusionConfig(
                get_or_default('entry-exclusions.config.removable-statuses', [])
            )
        )

        self.rewrite_rules = ConfiguredRewriteRules(
            get_or_default('rewrite-rules.response', []),
            get_or_default('rewrite-rules.request', []),
            RewriteRulesConfig(
                get_or_default('rewrite-rules.config.excluded-domains', []),
                get_or_default('rewrite-rules.config.removable-query-params', []),
                get_or_default('rewrite-rules.config.removable-request-headers', []),
                get_or_default('rewrite-rules.config.removable-response-headers', []),
                get_or_default('rewrite-rules.config.removable-request-cookies', [])
            )
        )

    def _get_or_default(self, options: Dict, key: str, default: T) -> T:
        try:
            segments = key.split('.')
            for i in range(len(segments) - 1):
                options = options[segments[i]]
            return options[segments[-1]]
        except:
            _log.info(f'Could not read property from config: [{key}]. Using default of [{default}]')
            return default

    def _curry_get_or_default(self, options: Dict) -> Callable[[str, T], T]:
        def get_or_default(key: str, default: T) -> T:
            return self._get_or_default(options, key, default)
        return get_or_default

    def _parse_config_yml(self, root_path: Path) -> Dict | None:
        config_path = root_path.joinpath('_config.yml')
        if not config_path.is_file():
            _log.info('No config file found. A config file named _config.yml can be added to the root of the '
                      '.har directory to customize the app behaviour.')
            return None

        _log.info(f'Loading configuration from file: [{config_path}]')
        with open(config_path, 'r', encoding='utf-8') as file:
            content = '\n'.join(file.readlines())
        return yaml.safe_load(content)
