import unittest
from unittest.mock import Mock, MagicMock, patch, PropertyMock

import copy

from server.core.config import ConfigLoader
from server.core.config.models import RequestRewriteRules
from server.core.rules.rewrite.request import (RequestRewriter, RequestRuleFailedException,
                                               RequestRuleNotFoundException)

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

        expected = Mock()
        mock_rule_1 = MagicMock(return_value=expected)
        mock_rule_2 = MagicMock()
        mock_rules.return_value = {
            _RULE_NAME: (mock_rule_1, mock_rule_2)
        }

        request_copy = Mock()
        mock_deep_copy.return_value = request_copy

        request = Mock()
        actual = RequestRewriter(mock_config_loader).apply_browser_request_rewrite_rules(request)

        self.assertEqual(expected, actual)

        mock_config_loader.read_config.assert_called_once_with(RequestRewriteRules)
        mock_deep_copy.assert_called_once_with(request)
        mock_rule_1.assert_called_once_with(mock_config_loader, request_copy)
        mock_rule_2.assert_not_called()

    @patch(fully_qualified_name(copy.deepcopy))
    @patch(fully_qualified_property_name(RequestRewriter, '_REQUEST_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_entry_request_rewrite_rules(self,
                                               mock_config_loader: ConfigLoader,
                                               mock_rules: MagicMock,
                                               mock_deep_copy: MagicMock):
        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

        expected = Mock()
        mock_rule_1 = MagicMock()
        mock_rule_2 = MagicMock(return_value=expected)
        mock_rules.return_value = {
            _RULE_NAME: (mock_rule_1, mock_rule_2)
        }

        request_copy = Mock()
        mock_deep_copy.return_value = request_copy

        request = Mock()
        actual = RequestRewriter(mock_config_loader).apply_entry_request_rewrite_rules(request)

        self.assertEqual(expected, actual)

        mock_config_loader.read_config.assert_called_once_with(RequestRewriteRules)
        mock_deep_copy.assert_called_once_with(request)
        mock_rule_1.assert_not_called()
        mock_rule_2.assert_called_once_with(mock_config_loader, request_copy)

    @patch(fully_qualified_name(copy.deepcopy))
    @patch(fully_qualified_property_name(RequestRewriter, '_REQUEST_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_browser_request_rewrite_rules_raises_exception_when_rule_raises_exception(self,
                                                                                             mock_config_loader: ConfigLoader,
                                                                                             mock_rules: MagicMock,
                                                                                             mock_deep_copy: MagicMock):
        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

        mock_rule_1 = MagicMock(side_effect=Exception())
        mock_rule_2 = MagicMock()
        mock_rules.return_value = {
            _RULE_NAME: (mock_rule_1, mock_rule_2)
        }

        request_copy = Mock()
        mock_deep_copy.return_value = request_copy

        request = Mock()
        with self.assertRaises(RequestRuleFailedException) as context:
            RequestRewriter(mock_config_loader).apply_browser_request_rewrite_rules(request)

        self.assertIn(_RULE_NAME, str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(RequestRewriteRules)
        mock_deep_copy.assert_called_once_with(request)
        mock_rule_1.assert_called_once_with(mock_config_loader, request_copy)
        mock_rule_2.assert_not_called()

    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_browser_request_rewrite_rules_raises_exception_when_rule_not_found(self,
                                                                                      mock_config_loader: ConfigLoader):
        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))

        with self.assertRaises(RequestRuleNotFoundException) as context:
            RequestRewriter(mock_config_loader).apply_browser_request_rewrite_rules(Mock())

        self.assertIn(_RULE_NAME, str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(RequestRewriteRules)
