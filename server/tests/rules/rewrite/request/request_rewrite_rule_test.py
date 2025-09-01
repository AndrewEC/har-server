import unittest
from unittest.mock import Mock, patch

from server.core.har import NameValuePair
from server.core.config import ConfigLoader, AppConfig
from server.core.rules.rewrite.request.rules import (
    RemoveQueryParamsRequestRewriteRule,
    RemoveCookieRequestRewriteRule,
    RemoveRequestHeaderRequestRewriteRule
)

from server.tests.util import fully_qualified_name


_REMOVABLE_PARAM = 'removable-param'
_NON_REMOVABLE_PARAM = 'non-removable-param'


class RequestRewriteRuleTest(unittest.TestCase):

    @patch(fully_qualified_name(ConfigLoader))
    def test_remove_query_param_from_entry_request(self, mock_config_loader: ConfigLoader):
        stub_config = AppConfig()
        stub_config.rewrite.request.config.removable_query_params = [_REMOVABLE_PARAM]
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        request = Mock(query_params=[
            NameValuePair(name=_REMOVABLE_PARAM, value='removable-value'),
            NameValuePair(name=_NON_REMOVABLE_PARAM, value='non-removable-value')
        ])

        rule = RemoveQueryParamsRequestRewriteRule()
        rule.initialize(mock_config_loader)
        request = rule.rewrite_incoming_http_request(request)

        self.assertEqual(1, len(request.query_params))
        self.assertEqual(_NON_REMOVABLE_PARAM, request.query_params[0].name)

        mock_config_loader.get_app_config.assert_called_once()

    @patch(fully_qualified_name(ConfigLoader))
    def test_remove_cookie_from_entry_request(self, mock_config_loader: ConfigLoader):
        stub_config = AppConfig()
        stub_config.rewrite.request.config.removable_cookies = [_REMOVABLE_PARAM]
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        request = Mock(cookies=[
            NameValuePair(name=_REMOVABLE_PARAM, value='removable-value'),
            NameValuePair(name=_NON_REMOVABLE_PARAM, value='non-removable-value')
        ])

        rule = RemoveCookieRequestRewriteRule()
        rule.initialize(mock_config_loader)
        request = rule.rewrite_incoming_http_request(request)

        self.assertEqual(1, len(request.cookies))
        self.assertEqual(_NON_REMOVABLE_PARAM, request.cookies[0].name)

        mock_config_loader.get_app_config.assert_called_once()

    @patch(fully_qualified_name(ConfigLoader))
    def test_remove_header_from_entry_request(self, mock_config_loader: ConfigLoader):
        stub_config = AppConfig()
        stub_config.rewrite.request.config.removable_headers = [_REMOVABLE_PARAM]
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        request = Mock(headers=[
            NameValuePair(name=_REMOVABLE_PARAM, value='removable-value'),
            NameValuePair(name=_NON_REMOVABLE_PARAM, value='non-removable-value')
        ])

        rule = RemoveRequestHeaderRequestRewriteRule()
        rule.initialize(mock_config_loader)
        request = rule.rewrite_incoming_http_request(request)

        self.assertEqual(1, len(request.headers))
        self.assertEqual(_NON_REMOVABLE_PARAM, request.headers[0].name)

        mock_config_loader.get_app_config.assert_called_once()
