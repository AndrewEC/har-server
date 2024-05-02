import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock

from server.core.config import ConfigLoader
from server.core.config.models import Matchers
from server.core.rules.matching import RequestMatcher, MatchRuleNotFound, MatchRuleFailedException

from server.tests.util import fully_qualified_name, fully_qualified_property_name


_RULE_NAME = 'test-rule'


class RequestMatcherTest(unittest.TestCase):

    @patch(fully_qualified_property_name(RequestMatcher, '_MATCHERS'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_do_requests_match(self, mock_config_loader: ConfigLoader, mock_rules: MagicMock):

        test_cases = [True, False]

        for test_case in test_cases:
            with self.subTest(expected=test_case):
                request = Mock()
                entry = Mock()

                mock_rule = MagicMock(return_value=test_case)

                mock_rules.return_value = {_RULE_NAME: mock_rule}
                mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

                actual = RequestMatcher(mock_config_loader).do_requests_match(entry, request)
                self.assertEqual(test_case, actual)

                mock_config_loader.read_config.assert_called_once_with(Matchers)
                mock_rule.assert_called_once_with(mock_config_loader, entry, request)

    @patch(fully_qualified_name(ConfigLoader))
    def test_do_request_match_raises_exception_when_match_rule_is_not_found(self, mock_config_loader: ConfigLoader):
        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=['invalid-rule']))

        with self.assertRaises(MatchRuleNotFound) as context:
            RequestMatcher(mock_config_loader).do_requests_match(Mock(), Mock())

        self.assertIn('invalid-rule', str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(Matchers)

    @patch(fully_qualified_property_name(RequestMatcher, '_MATCHERS'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_do_requests_match_raises_exception_when_rule_raises_exception(self,
                                                                           mock_config_loader: ConfigLoader,
                                                                           mock_rules: MagicMock):
        mock_rule = MagicMock(side_effect=Exception())
        mock_rules.return_value = {_RULE_NAME: mock_rule}
        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

        with self.assertRaises(MatchRuleFailedException) as context:
            RequestMatcher(mock_config_loader).do_requests_match(Mock(), Mock())

        self.assertIn(_RULE_NAME, str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(Matchers)
