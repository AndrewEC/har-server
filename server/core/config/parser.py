from typing import Dict
from functools import lru_cache
import logging

import yaml

from .root import get_root_path

_log = logging.getLogger(__file__)


class ConfigParser:

    def parse_config_yml(self) -> Dict | None:
        config_path = get_root_path().joinpath('_config.yml')
        if not config_path.is_file():
            _log.info('No config file found. A config file named _config.yml can be added to the root of the '
                      '.har directory to customize the app behaviour.')
            return None

        _log.info(f'Loading configuration from file: [{config_path}]')
        with open(config_path, 'r', encoding='utf-8') as file:
            content = '\n'.join(file.readlines())
        return yaml.safe_load(content)


@lru_cache()
def with_config_parser() -> ConfigParser:
    return ConfigParser()
