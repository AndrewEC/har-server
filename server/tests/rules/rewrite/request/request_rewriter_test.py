import unittest
from unittest.mock import Mock, MagicMock, patch, PropertyMock

import copy

from server.core.config import ConfigLoader
from server.core.config.models import RequestRewriteRules
from server.core.rules.rewrite.request import RequestRewriter
from server.core.rules.base import RuleFailedException

from server.tests.util import fully_qualified_name, fully_qualified_property_name


_RULE_NAME = 'test-rule'


class RequestRewriterTest(unittest.TestCase):

    @patch(fully_qualified_name(copy.deepcopy))
    @patch(fully_qualified_property_name(RequestRewriter, '_REQUEST_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_browser_request_rewrite_rules(self,
                                                 mock_config_loader: ConfigLoader,
                                                 mock_rules: MagicMock,
                                                 mock_deep_copy: MagicMock):

        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

        request_copy = Mock()
        mock_deep_copy.return_value = request_copy

        expected = Mock()
        mock_rule = Mock(
            get_name=MagicMock(return_value=_RULE_NAME),
            rewrite_incoming_http_request=MagicMock(return_value=expected),
            rewrite_har_entry_request=MagicMock()
        )
        mock_rules.return_value = [MagicMock(return_value=mock_rule)]

        request = Mock()
        actual = RequestRewriter(mock_config_loader).apply_browser_request_rewrite_rules(request)

        self.assertEqual(expected, actual)

        mock_config_loader.read_config.assert_called_once_with(RequestRewriteRules)
        mock_deep_copy.assert_called_once_with(request)
        mock_rule.rewrite_incoming_http_request.assert_called_once_with(request_copy)
        mock_rule.rewrite_har_entry_request.assert_not_called()

    @patch(fully_qualified_name(copy.deepcopy))
    @patch(fully_qualified_property_name(RequestRewriter, '_REQUEST_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_entry_request_rewrite_rules(self,
                                               mock_config_loader: ConfigLoader,
                                               mock_rules: MagicMock,
                                               mock_deep_copy: MagicMock):
        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

        expected = Mock()
        mock_rule = Mock(
            get_name=MagicMock(return_value=_RULE_NAME),
            rewrite_incoming_http_request=MagicMock(),
            rewrite_har_entry_request=MagicMock(return_value=expected)
        )
        mock_rules.return_value = [MagicMock(return_value=mock_rule)]

        request_copy = Mock()
        mock_deep_copy.return_value = request_copy

        request = Mock()
        actual = RequestRewriter(mock_config_loader).apply_entry_request_rewrite_rules(request)

        self.assertEqual(expected, actual)

        mock_config_loader.read_config.assert_called_once_with(RequestRewriteRules)
        mock_deep_copy.assert_called_once_with(request)
        mock_rule.rewrite_har_entry_request.assert_called_once_with(request_copy)
        mock_rule.rewrite_incoming_http_request.assert_not_called()

    @patch(fully_qualified_name(copy.deepcopy))
    @patch(fully_qualified_property_name(RequestRewriter, '_REQUEST_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_browser_request_rewrite_rules_raises_exception_when_rule_raises_exception(self,
                                                                                             mock_config_loader: ConfigLoader,
                                                                                             mock_rules: MagicMock,
                                                                                             mock_deep_copy: MagicMock):
        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

        mock_rule = Mock(
            get_name=MagicMock(return_value=_RULE_NAME),
            rewrite_incoming_http_request=MagicMock(side_effect=Exception()),
            rewrite_har_entry_request=MagicMock()
        )
        mock_rules.return_value = [MagicMock(return_value=mock_rule)]

        request_copy = Mock()
        mock_deep_copy.return_value = request_copy

        request = Mock()
        with self.assertRaises(RuleFailedException) as context:
            RequestRewriter(mock_config_loader).apply_browser_request_rewrite_rules(request)

        self.assertIn(_RULE_NAME, str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(RequestRewriteRules)
        mock_deep_copy.assert_called_once_with(request)
        mock_rule.rewrite_incoming_http_request.assert_called_once_with(request_copy)
        mock_rule.rewrite_har_entry_request.assert_not_called()
