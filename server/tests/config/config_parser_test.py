from typing import Dict, Any
import unittest
from pathlib import Path

from server.core.config import set_root_path, ConfigParser


class ConfigParserTests(unittest.TestCase):

    _EXPECTED_NAME = 'expected_name'
    _EXPECTED_VALUE = 'Expected Value'

    def test_parse_config_yml(self):
        set_root_path(Path(__file__).absolute().parent)

        config: Dict[Any, Any] = ConfigParser().parse_config_yml() # type: ignore

        self.assertIsNotNone(config)
        self.assertIn(ConfigParserTests._EXPECTED_NAME, config)
        self.assertEqual(ConfigParserTests._EXPECTED_VALUE, config[ConfigParserTests._EXPECTED_NAME])

    def test_parse_config_yml_returns_none_if_file_is_missing(self):
        set_root_path(Path(__file__).absolute().parent.parent)

        actual = ConfigParser().parse_config_yml()

        self.assertIsNone(actual)
