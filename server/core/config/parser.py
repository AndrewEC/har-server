from typing import Dict
from functools import lru_cache
import logging
import copy

import yaml

from .root import get_root_path

_log = logging.getLogger(__file__)


class ConfigParser:

    def __init__(self):
        self._cached_contents = None

    def parse_config_yml(self) -> Dict | None:
        """
        Attempts to parse the yml configuration file.

        If the file has been previously parsed this will return a copy of the cached version of the parsed file
        contents.

        If no configuration file exists in the applications root_path this will return None.

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
