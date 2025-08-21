import unittest
from unittest.mock import Mock, patch

from server.core.config import ConfigLoader, AppConfig
from server.core.rules.rewrite.response.rules import RewriteUrlResponseRewriteRule

from server.tests.util import fully_qualified_name


_CONTENT_TEMPLATE = 'Replace url ({}) with localhost.'
_LOCALHOST = 'http://localhost:8080'


class RewriteUrlResponseRewriteRuleTest(unittest.TestCase):

    @patch(fully_qualified_name(ConfigLoader))
    def test_rewrite_response_content_urls(self, mock_config_loader: ConfigLoader):

        stub_config = AppConfig()
        stub_config.rewrite.response.config.excluded_domains = []
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        test_cases = [
            'https://www.mock.ca',
            'https://www.mock.ca:443',
            'http://www.mock.com',
            'http://www.mock.com:443',
            '//www.mock.com',
            '//www.mock.com:443',
            'http://subdomain.mock.com'
        ]

        for test_case in test_cases:
            with self.subTest(origin=test_case):
                mock_config_loader.get_app_config.reset_mock()

                response = Mock(content=Mock(text=_CONTENT_TEMPLATE.format(test_case)))
                rule = RewriteUrlResponseRewriteRule()
                rule.initialize(mock_config_loader)
                actual = rule.rewrite_response(response)

                expected = _CONTENT_TEMPLATE.format(_LOCALHOST)
                self.assertEqual(expected, actual.content.text)

                mock_config_loader.get_app_config.assert_called_once()

    @patch(fully_qualified_name(ConfigLoader))
    def test_rewrite_response_content_urls_replaces_nothing_when_no_origin_is_found(self, mock_config_loader: ConfigLoader):

        stub_config = AppConfig()
        stub_config.rewrite.response.config.excluded_domains = []
        mock_config_loader.get_app_config = Mock(return_value=stub_config)

        test_cases = [
            '//.',
            'http://-',
            'https://-',
            'http://.',
            'https://.',
            'http://:',
            'https://:',
            'http://wwwmockcom',
            'httpwwwmockcom',
        ]

        for test_case in test_cases:
            with self.subTest(origin=test_case):
                mock_config_loader.get_app_config.reset_mock()

                expected = _CONTENT_TEMPLATE.format(test_case)
                response = Mock(content=Mock(text=expected))

                rule = RewriteUrlResponseRewriteRule()
                rule.initialize(mock_config_loader)
                actual = rule.rewrite_response(response)

                self.assertEqual(expected, actual.content.text)

                mock_config_loader.get_app_config.assert_called_once()
