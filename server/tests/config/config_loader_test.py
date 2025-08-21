import unittest
from unittest.mock import Mock, patch

from server.core.config import ConfigLoader, ConfigParser

from server.tests.util import fully_qualified_name


_FIRST_RULE_VALUE = 'first_rule'
_SECOND_RULE_VALUE = 'second_rule'


class ConfigLoaderTests(unittest.TestCase):

    @patch(fully_qualified_name(ConfigParser))
    def test_read_config(self, mock_config_parser: ConfigParser):
        stub_config = {
            'request-matching': {
                'rules': [_FIRST_RULE_VALUE, _SECOND_RULE_VALUE]
            }
        }

        mock_config_parser.parse_config_yml = Mock(return_value=stub_config)

        actual = ConfigLoader(mock_config_parser).get_app_config()
        rules = actual.request_matching.rules

        self.assertTrue(_FIRST_RULE_VALUE in rules)
        self.assertTrue(_SECOND_RULE_VALUE in rules)
        self.assertEqual(2, len(rules))

        mock_config_parser.parse_config_yml.assert_called_once()
