import unittest
from unittest.mock import Mock, patch, PropertyMock, MagicMock

from server.core.config import ConfigLoader, AppConfig
from server.core.har.models import NameValuePair
from server.core.rules.rewrite.request import RequestRewriter
from server.core.rules.base import RuleFailedException

from server.tests.util import fully_qualified_name, fully_qualified_property_name


_RULE_NAME = 'test-rule'


class RequestRewriterTest(unittest.TestCase):

    @patch(fully_qualified_property_name(RequestRewriter, '_REQUEST_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_browser_request_rewrite_rules(self,
                                                 mock_config_loader: ConfigLoader,
                                                 mock_rules: Mock):

        stub_config = AppConfig()
        stub_config.rewrite.request.rules = [_RULE_NAME]
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        expected_request = MagicMock(
            query_params=[NameValuePair(name='query_name', value='query_value')],
            headers=[NameValuePair(name='header_name', value='header_value')],
            cookies=[NameValuePair(name='cookie_name', value='cookie_value')],
            post_data=MagicMock(mime_type='application/x-www-form-urlencoded', params=[NameValuePair(name='body_name', value='body_value')])
        )

        mock_rule = Mock(
            get_name=Mock(return_value=_RULE_NAME),
            rewrite_incoming_http_request=Mock(return_value=expected_request),
            rewrite_har_entry_request=Mock()
        )
        mock_rules.return_value = [Mock(return_value=mock_rule)]

        request = Mock()
        actual = RequestRewriter(mock_config_loader).apply_browser_request_rewrite_rules(request)

        self.assertEqual(expected_request, actual)
        self.assertEqual(str(hash('query_name=query_value')), actual.hashes.query_params)
        self.assertEqual(str(hash('cookie_name=cookie_value')), actual.hashes.cookies)
        self.assertEqual(str(hash('header_name=header_value')), actual.hashes.headers)
        self.assertEqual(str(hash('body_name=body_value')), actual.hashes.post_data)

        mock_config_loader.get_app_config.assert_called_once()
        mock_rule.rewrite_incoming_http_request.assert_called_once_with(request)
        mock_rule.rewrite_har_entry_request.assert_not_called()

    @patch(fully_qualified_property_name(RequestRewriter, '_REQUEST_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_entry_request_rewrite_rules(self,
                                               mock_config_loader: ConfigLoader,
                                               mock_rules: Mock):
        stub_config = AppConfig()
        stub_config.rewrite.request.rules = [_RULE_NAME]
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        expected_request = MagicMock(
            query_params=[NameValuePair(name='query_name', value='query_value')],
            headers=[NameValuePair(name='header_name', value='header_value')],
            cookies=[NameValuePair(name='cookie_name', value='cookie_value')],
            post_data=MagicMock(mime_type='application/x-www-form-urlencoded', params=[NameValuePair(name='body_name', value='body_value')])
        )

        mock_rule = Mock(
            get_name=Mock(return_value=_RULE_NAME),
            rewrite_incoming_http_request=Mock(),
            rewrite_har_entry_request=Mock(return_value=expected_request)
        )
        mock_rules.return_value = [Mock(return_value=mock_rule)]

        request = Mock()
        actual = RequestRewriter(mock_config_loader).apply_entry_request_rewrite_rules(request)

        self.assertEqual(expected_request, actual)
        self.assertEqual(str(hash('query_name=query_value')), actual.hashes.query_params)
        self.assertEqual(str(hash('cookie_name=cookie_value')), actual.hashes.cookies)
        self.assertEqual(str(hash('header_name=header_value')), actual.hashes.headers)
        self.assertEqual(str(hash('body_name=body_value')), actual.hashes.post_data)

        mock_config_loader.get_app_config.assert_called_once()
        mock_rule.rewrite_har_entry_request.assert_called_once_with(request)
        mock_rule.rewrite_incoming_http_request.assert_not_called()

    @patch(fully_qualified_property_name(RequestRewriter, '_REQUEST_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_browser_request_rewrite_rules_raises_exception_when_rule_raises_exception(self,
                                                                                             mock_config_loader: ConfigLoader,
                                                                                             mock_rules: Mock):
        stub_config = AppConfig()
        stub_config.rewrite.request.rules = [_RULE_NAME]
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        mock_rule = Mock(
            get_name=Mock(return_value=_RULE_NAME),
            rewrite_incoming_http_request=Mock(side_effect=Exception()),
            rewrite_har_entry_request=Mock()
        )
        mock_rules.return_value = [Mock(return_value=mock_rule)]

        request = Mock()
        with self.assertRaises(RuleFailedException) as context:
            RequestRewriter(mock_config_loader).apply_browser_request_rewrite_rules(request)

        self.assertIn(_RULE_NAME, str(context.exception))

        mock_config_loader.get_app_config.assert_called_once()
        mock_rule.rewrite_incoming_http_request.assert_called_once_with(request)
        mock_rule.rewrite_har_entry_request.assert_not_called()
