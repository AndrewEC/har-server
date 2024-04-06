from typing import List, Dict, TypeVar
import logging
from pathlib import Path
import yaml


_log = logging.getLogger(__file__)
T = TypeVar('T')


def _get_or_default(options: Dict, key: str, default: T) -> T:
    try:
        segments = key.split('.')
        for i in range(len(segments) - 1):
            options = options[segments[i]]
        return options[segments[-1]]
    except:
        _log.info(f'Could not read property from config: [{key}].')
        return default


class ConfigException(Exception):

    def __init__(self, message: str, e: Exception):
        super().__init__(message, e)


class RewriteRulesConfig:

    def __init__(self, excluded_domains: List[str] = [], removable_query_params: List[str] = [],
                 removable_request_headers: List[str] = [], removable_response_headers: List[str] = []):
        self.excluded_domains = excluded_domains
        self.removable_query_params = removable_query_params
        self.removable_request_headers = removable_request_headers
        self.removable_response_headers = removable_response_headers


class ConfiguredRewriteRules:

    def __init__(self, response_rules: List[str] = [], request_rules: List[str] = [],
                 rule_config: RewriteRulesConfig = RewriteRulesConfig()):
        self.response_rules = response_rules
        self.request_rules = request_rules
        self.rule_config = rule_config


class ExclusionConfig:

    def __init__(self, bad_statuses: List[int] = []):
        self.bad_statuses = bad_statuses


class ConfiguredExclusions:

    def __init__(self, rules: List[str] = [], exclusion_config: ExclusionConfig = ExclusionConfig()):
        self.rules = rules
        self.exclusion_config = exclusion_config


class MatchConfig:

    def __init__(self):
        pass


class Matching:

    def __init__(self, rules: List[str] = [], match_config: MatchConfig = MatchConfig):
        self.rules = rules
        self.match_config = match_config


class Debug:

    def __init__(self, log_stack = False, dump_urls = False):
        self.log_stack = log_stack
        self.dump_urls = dump_urls


class Config:

    """
    Global configuration class intended to parse and hold the configuration values from the default
    _config.yml configuration file.
    """

    def __init__(self):
        self.debug = Debug()
        self.port = 8000
        self.exclusions = ConfiguredExclusions()
        self.rewrite_rules = ConfiguredRewriteRules()
        self.matching = Matching()

    def load(self, root_path: Path):
        """
        Parses the _config.yml file from the har directory specified when running the har-server.

        If no _config.yml file can be found this will effectively do nothing.

        :param root_path: The path to the directory containing the _config.yml file.
        :raise: ConfigException if an any error occurs while trying to parse the config file.
        """
        try:
            self._do_load(root_path)
        except Exception as e:
            raise ConfigException('Could not load configuration from _config.yml file.', e)

    def _do_load(self, root_path: Path):
        parsed = self._parse_config_yml(root_path)
        if parsed is None:
            return

        self.debug = Debug(
            _get_or_default(parsed, 'debug.log-stack-traces', False),
            _get_or_default(parsed, 'debug.dump-urls', False)
        )
        self.port = _get_or_default(parsed, 'server.port', 8000)

        self.matching = Matching(
            _get_or_default(parsed, 'request-matching.rules', []),
            MatchConfig()
        )

        self.exclusions = ConfiguredExclusions(
            _get_or_default(parsed, 'entry-exclusions.rules', []),
            ExclusionConfig(
                _get_or_default(parsed, 'entry-exclusions.config.bad-statuses', [])
            )
        )

        self.rewrite_rules = ConfiguredRewriteRules(
            _get_or_default(parsed, 'rewrite-rules.response', []),
            _get_or_default(parsed, 'rewrite-rules.request', []),
            RewriteRulesConfig(
                _get_or_default(parsed, 'rewrite-rules.config.excluded-domains', []),
                _get_or_default(parsed, 'rewrite-rules.config.removable-query-params', []),
                _get_or_default(parsed, 'rewrite-rules.config.removable-request-headers', []),
                _get_or_default(parsed, 'rewrite-rules.config.removable-response-headers', [])
            )
        )

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
