from typing import Dict, Any
from functools import lru_cache
import logging
import copy

import yaml

from .root import get_root_path

_log = logging.getLogger(__file__)


class ConfigParser:

    def __init__(self):
        self._cached_contents: Dict[Any, Any] | None = None

    def parse_config_yml(self) -> Dict[Any, Any] | None:
        """
        Attempts to parse the yml configuration file.

        If no configuration file exists within the root of the folder the
        user specified when starting the app this will return None.

        :return: The parsed contents of the configuration file.
        """
        if self._cached_contents is not None:
            return copy.deepcopy(self._cached_contents)

        config_path = get_root_path().joinpath('_config.yml')
        if not config_path.is_file():
            _log.info('No config file found. A config file named _config.yml can be added to the root of the '
                      '.har directory to customize the app behaviour.')
            return None

        _log.info(f'Loading configuration from file: [{config_path}]')
        with open(config_path, 'r', encoding='utf-8') as file:
            content = '\n'.join(file.readlines())

        self._cached_contents = yaml.safe_load(content)
        return copy.deepcopy(self._cached_contents)


@lru_cache()
def with_config_parser() -> ConfigParser:
    return ConfigParser()
