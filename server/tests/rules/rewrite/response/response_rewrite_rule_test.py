import unittest
from unittest.mock import Mock, patch

from server.core.har import NameValuePair
from server.core.config import ConfigLoader, AppConfig
from server.core.rules.rewrite.response.rules import (
    RemoveHeaderResponseRewriteRule,
    RemoveCookiesResponseRewriteRule
)

from server.tests.util import fully_qualified_name


_REMOVABLE_NAME = 'removable-name'
_NON_REMOVABLE_NAME = 'non-removable-name'


class ResponseRewriteRuleTest(unittest.TestCase):

    @patch(fully_qualified_name(ConfigLoader))
    def test_remove_cookies_from_response(self, mock_config_loader: ConfigLoader):
        stub_config = AppConfig()
        stub_config.rewrite.response.config.removable_cookies = [_REMOVABLE_NAME]
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        response = Mock(cookies=[
            NameValuePair(name=_REMOVABLE_NAME, value='removable-value'),
            NameValuePair(name=_NON_REMOVABLE_NAME, value='non-removable-value')
        ])

        rule = RemoveCookiesResponseRewriteRule()
        rule.initialize(mock_config_loader)
        actual = rule.rewrite_response(response)

        self.assertEqual(1, len(actual.cookies))
        self.assertEqual(_NON_REMOVABLE_NAME, actual.cookies[0].name)

        mock_config_loader.get_app_config.assert_called_once()

    @patch(fully_qualified_name(ConfigLoader))
    def test_remove_headers_from_response(self, mock_config_loader: ConfigLoader):
        stub_config = AppConfig()
        stub_config.rewrite.response.config.removable_headers = [_REMOVABLE_NAME]
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        response = Mock(headers=[
            NameValuePair(name=_REMOVABLE_NAME, value='removable-value'),
            NameValuePair(name=_NON_REMOVABLE_NAME, value='non-removable-value')
        ])

        rule = RemoveHeaderResponseRewriteRule()
        rule.initialize(mock_config_loader)
        actual = rule.rewrite_response(response)

        self.assertEqual(1, len(actual.headers))
        self.assertEqual(_NON_REMOVABLE_NAME, actual.headers[0].name)

        mock_config_loader.get_app_config.assert_called_once()
