import unittest
from unittest.mock import patch, Mock, MagicMock, PropertyMock

from server.core.config import ConfigLoader
from server.core.config.models import Matchers
from server.core.rules.matching import RequestMatcher
from server.core.rules.base import RuleFailedException

from server.tests.util import fully_qualified_name, fully_qualified_property_name


_RULE_NAME = 'test-rule'


class RequestMatcherTest(unittest.TestCase):

    @patch(fully_qualified_property_name(RequestMatcher, '_MATCHERS'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_do_requests_match(self, mock_config_loader: ConfigLoader, mock_rules: MagicMock):

        for test_case in [True, False]:
            with self.subTest(expected=test_case):
                request = Mock()
                entry = Mock()

                mock_rule = Mock(
                    get_name=MagicMock(return_value=_RULE_NAME),
                    matches=MagicMock(return_value=test_case)
                )
                mock_rule_type = MagicMock(return_value=mock_rule)

                mock_rules.return_value = [mock_rule_type]
                mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

                actual = RequestMatcher(mock_config_loader).do_requests_match(entry, request)
                self.assertEqual(test_case, actual)

                mock_config_loader.read_config.assert_called_once_with(Matchers)
                mock_rule.matches.assert_called_once_with(entry, request)

    @patch(fully_qualified_property_name(RequestMatcher, '_MATCHERS'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_do_requests_match_raises_exception_when_rule_raises_exception(self,
                                                                           mock_config_loader: ConfigLoader,
                                                                           mock_rules: MagicMock):
        mock_rule = Mock(
            get_name=MagicMock(return_value=_RULE_NAME),
            matches=MagicMock(side_effect=Exception())
        )
        mock_rule_type = MagicMock(return_value=mock_rule)

        mock_rules.return_value = [mock_rule_type]
        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

        with self.assertRaises(RuleFailedException) as context:
            RequestMatcher(mock_config_loader).do_requests_match(Mock(), Mock())

        self.assertIn(_RULE_NAME, str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(Matchers)
