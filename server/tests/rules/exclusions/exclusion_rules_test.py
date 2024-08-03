import unittest
from unittest.mock import Mock, MagicMock, patch

from server.core.config import ConfigLoader
from server.core.config.models import ExclusionConfig
from server.core.rules.exclusions.rules import (bad_status_exclusion_rule, invalid_size_exclusion_rule,
                                                http_method_exclusion_rule)

from server.tests.util import fully_qualified_name


class ExclusionRuleTest(unittest.TestCase):

    @patch(fully_qualified_name(ConfigLoader))
    def test_http_method_exclusion_rule(self, mock_config_loader: ConfigLoader):
        test_cases = [(False, 'POST'), (True, 'HEAD')]

        for test_case in test_cases:
            with self.subTest(method=test_case[1]):
                mock_config_loader.read_config = MagicMock(return_value=Mock(removable_http_methods=['HEAD']))

                entry = Mock(
                    request=Mock(
                        method=test_case[1]
                    )
                )

                actual = http_method_exclusion_rule(mock_config_loader, entry)

                self.assertEqual(test_case[0], actual)

                mock_config_loader.read_config.assert_called_once_with(ExclusionConfig)

    @patch(fully_qualified_name(ConfigLoader))
    def test_bad_status_exclusion_rule(self, mock_config_loader: ConfigLoader):
        test_cases = [(False, 200), (True, 304)]

        for test_case in test_cases:
            with self.subTest(status=test_case[1], filter_out=test_case[0]):
                mock_config_loader.read_config = MagicMock(return_value=Mock(removable_statuses=[304]))

                entry = Mock(
                    response=Mock(
                        status=test_case[1]
                    )
                )

                actual = bad_status_exclusion_rule(mock_config_loader, entry)

                self.assertEqual(test_case[0], actual)

                mock_config_loader.read_config.assert_called_once_with(ExclusionConfig)

    def test_invalid_size_exclusion_rule(self):
        test_cases = [
            (False, 204, ''),
            (False, 200, 'test_response'),
            (True, 200, ''),
            (True, 204, 'test_response')
        ]

        for test_case in test_cases:
            with self.subTest(status=test_case[1], should_filter=test_case[0]):
                entry = Mock(
                    response=Mock(
                        status=test_case[1],
                        content=Mock(
                            text=test_case[2]
                        )
                    )
                )
                actual = invalid_size_exclusion_rule(None, entry)
                self.assertEqual(test_case[0], actual)
