from typing import Dict, Any, Annotated
import logging
from functools import lru_cache
import copy

from fastapi import Depends

from .models import AppConfig
from .config_parser import ConfigParser, with_config_parser


_log = logging.getLogger(__file__)


class ConfigLoader:

    def __init__(self, config_parser: ConfigParser):
        user_defined_config = config_parser.parse_config_yml()
        if user_defined_config is not None:
            updated_config = self._rewrite_keys(user_defined_config)
            _log.info(f'Loading user defined app config of: [{updated_config}].')
            self._app_config = AppConfig(**updated_config)
        else:
            _log.info('No user defined app config provided. Loading default app config.')
            self._app_config = AppConfig()

    def _rewrite_keys(self, config: Dict[Any, Any]) -> Dict[Any, Any]:
        """
        Updates all keys in the dictionary by replacing hyphens with underscores.

        This allows users to name yaml properties in their config using either
        underscores or hyphen such as enable_debug_logs or enable-debug-logs.
        """
        updated: Dict[Any, Any] = dict()

        for key, value in config.items():
            updated[key.replace('-', '_')] = value

            if isinstance(value, dict):
                updated[key] = self._rewrite_keys(value)  # type: ignore

        return updated

    def get_app_config(self) -> AppConfig:
        return copy.deepcopy(self._app_config)


@lru_cache()
def with_config_loader(parser: Annotated[ConfigParser, Depends(with_config_parser)]) -> ConfigLoader:
    return ConfigLoader(parser)
