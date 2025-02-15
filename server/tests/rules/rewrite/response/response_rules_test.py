import unittest
from unittest.mock import Mock, patch

from server.core.config import ConfigLoader
from server.core.config.models import ResponseRuleConfig
from server.core.rules.rewrite.response.rules import RemoveResponseHeaderRewriteRule, RemoveCookiesResponseRewriteRule

from server.tests.util import fully_qualified_name


_REMOVABLE_NAME = 'removable-name'
_NON_REMOVABLE_NAME = 'non-removable-name'


class ResponseRewriteRulesTest(unittest.TestCase):

    @patch(fully_qualified_name(ConfigLoader))
    def test_remove_cookies_from_response(self, mock_config_loader: ConfigLoader):
        mock_config_loader.read_config = Mock(return_value=Mock(removable_cookies=[_REMOVABLE_NAME]))

        response = Mock(cookies={
            _REMOVABLE_NAME: 'removable-value',
            _NON_REMOVABLE_NAME: 'non-removable-value'
        })

        rule = RemoveCookiesResponseRewriteRule()
        rule.initialize(mock_config_loader)
        actual = rule.rewrite_response(response)

        self.assertNotIn(_REMOVABLE_NAME, actual.cookies)
        self.assertIn(_NON_REMOVABLE_NAME, actual.cookies)

        mock_config_loader.read_config.assert_called_once_with(ResponseRuleConfig)

    @patch(fully_qualified_name(ConfigLoader))
    def test_remove_headers_from_response(self, mock_config_loader: ConfigLoader):
        mock_config_loader.read_config = Mock(return_value=Mock(removable_headers=[_REMOVABLE_NAME]))

        response = Mock(headers={
            _REMOVABLE_NAME: 'removable-value',
            _NON_REMOVABLE_NAME: 'non-removable-value'
        })

        rule = RemoveResponseHeaderRewriteRule()
        rule.initialize(mock_config_loader)
        actual = rule.rewrite_response(response)

        self.assertNotIn(_REMOVABLE_NAME, actual.headers)
        self.assertIn(_NON_REMOVABLE_NAME, actual.headers)

        mock_config_loader.read_config.assert_called_once_with(ResponseRuleConfig)
