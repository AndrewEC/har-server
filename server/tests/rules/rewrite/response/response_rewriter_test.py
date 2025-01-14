import unittest
from unittest.mock import Mock, patch, PropertyMock

import copy

from server.core.config import ConfigLoader
from server.core.config.models import ResponseRewriteRules
from server.core.rules.rewrite.response import ResponseRewriter
from server.core.rules.base import RuleFailedException

from server.tests.util import fully_qualified_name, fully_qualified_property_name


_RULE_NAME = 'test-rule'


class ResponseRewriterTest(unittest.TestCase):

    @patch(fully_qualified_name(copy.deepcopy))
    @patch(fully_qualified_property_name(ResponseRewriter, '_RESPONSE_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_response_rewrite_rules(self,
                                          mock_config_loader: ConfigLoader,
                                          mock_rules: Mock,
                                          mock_deep_copy: Mock):

        response = Mock()
        response_copy = Mock()
        mock_deep_copy.return_value = response_copy

        expected = Mock()
        mock_rule = Mock(
            get_name=Mock(return_value=_RULE_NAME),
            rewrite_response=Mock(return_value=expected)
        )
        mock_rules.return_value = [Mock(return_value=mock_rule)]

        mock_config_loader.read_config = Mock(return_value=Mock(rules=[_RULE_NAME]))

        actual = ResponseRewriter(mock_config_loader).apply_response_rewrite_rules(response)

        self.assertEqual(expected, actual)

        mock_config_loader.read_config.assert_called_once_with(ResponseRewriteRules)
        mock_deep_copy.assert_called_once_with(response)
        mock_rule.rewrite_response.assert_called_once_with(response_copy)

    @patch(fully_qualified_name(copy.deepcopy))
    @patch(fully_qualified_property_name(ResponseRewriter, '_RESPONSE_REWRITE_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_apply_response_rewrite_rules_raises_exception_when_rule_raises_exception(self,
                                                                                      mock_config_loader: ConfigLoader,
                                                                                      mock_rules: Mock,
                                                                                      mock_deep_copy: Mock):
        response = Mock()
        response_copy = Mock()
        mock_deep_copy.return_value = response_copy

        mock_rule = Mock(
            get_name=Mock(return_value=_RULE_NAME),
            rewrite_response=Mock(side_effect=Exception())
        )
        mock_rules.return_value = [Mock(return_value=mock_rule)]

        mock_config_loader.read_config = Mock(return_value=Mock(rules=[_RULE_NAME]))

        with self.assertRaises(RuleFailedException) as context:
            ResponseRewriter(mock_config_loader).apply_response_rewrite_rules(response)

        self.assertIn(_RULE_NAME, str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(ResponseRewriteRules)
        mock_deep_copy.assert_called_once_with(response)
        mock_rule.rewrite_response.assert_called_once_with(response_copy)
