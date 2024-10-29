import unittest
from unittest.mock import Mock, MagicMock, patch

from server.core.config.models import ResponseRuleConfig
from server.core.config import ConfigLoader
from server.core.rules.rewrite.response.rules import ResponseContentUrlResponseRewriteRules

from server.tests.util import fully_qualified_name


_CONTENT_TEMPLATE = 'Replace url ({}) with localhost.'
_LOCALHOST = 'http://localhost:8080'


class ResponseContentUrlTest(unittest.TestCase):

    @patch(fully_qualified_name(ConfigLoader))
    def test_rewrite_response_content_urls(self, mock_config_loader: ConfigLoader):
        mock_config_loader.read_config = MagicMock(return_value=Mock(excluded_domains=[]))

        test_cases = [
            'https://www.google.ca',
            'https://www.google.ca:443',
            'http://www.test.com',
            'http://www.testing.com:443',
            '//www.mock.com',
            '//www.mock.com:443'
        ]

        for test_case in test_cases:
            with self.subTest(origin=test_case):
                mock_config_loader.read_config.reset_mock()

                response = Mock(content=Mock(text=_CONTENT_TEMPLATE.format(test_case)))
                rule = ResponseContentUrlResponseRewriteRules()
                rule.initialize(mock_config_loader)
                actual = rule.rewrite_response(response)

                expected = _CONTENT_TEMPLATE.format(_LOCALHOST)
                self.assertEqual(expected, actual.content.text)

                mock_config_loader.read_config.assert_called_once_with(ResponseRuleConfig)

    @patch(fully_qualified_name(ConfigLoader))
    def test_rewrite_response_content_urls_negative_cases(self, mock_config_loader: ConfigLoader):
        mock_config_loader.read_config = MagicMock(return_value=Mock(excluded_domains=['http://www.google.com']))

        test_cases = [
            '//.',
            'http://-',
            'https://-',
            'http://.',
            'https://.',
            'http://:',
            'https://:',
            'http://wwwgooglecom',
            'http://www.google.com:',
            'httpwwwgooglecom',
        ]

        for test_case in test_cases:
            with self.subTest(origin=test_case):
                mock_config_loader.read_config.reset_mock()

                expected = _CONTENT_TEMPLATE.format(test_case)
                response = Mock(content=Mock(text=expected))

                rule = ResponseContentUrlResponseRewriteRules()
                rule.initialize(mock_config_loader)
                actual = rule.rewrite_response(response)

                self.assertEqual(expected, actual.content.text)

                mock_config_loader.read_config.assert_called_once_with(ResponseRuleConfig)
