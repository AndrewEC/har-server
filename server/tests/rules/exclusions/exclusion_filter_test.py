import unittest
from unittest.mock import Mock, MagicMock, patch, PropertyMock

from server.core.config import ConfigLoader
from server.core.config.models import ExclusionRules
from server.core.rules.exclusions import (ExclusionFilter, EntryExclusionRuleNotFoundException,
                                          ExclusionRuleFailedException)

from server.tests.util import fully_qualified_name, fully_qualified_property_name


_RULE_NAME = 'test-rule'


class ExclusionFilterTest(unittest.TestCase):

    @patch(fully_qualified_property_name(ExclusionFilter, '_EXCLUSION_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_should_exclude_entry(self,
                                  mock_config_loader: ConfigLoader,
                                  mock_rules: MagicMock):

        results = [True, False]

        for result in results:
            with self.subTest(should_filter=result):
                mock_config_loader.read_config.reset_mock()

                mock_rule = MagicMock()
                mock_rules.return_value = {_RULE_NAME: mock_rule}

                mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))
                mock_rule.return_value = result

                entry = Mock()
                actual = ExclusionFilter(mock_config_loader).should_exclude_entry(entry)
                self.assertEqual(result, actual)

                mock_config_loader.read_config.assert_called_once_with(ExclusionRules)
                mock_rule.assert_called_once_with(mock_config_loader, entry)

    @patch(fully_qualified_name(ConfigLoader))
    def test_should_exclude_entry_raises_exception_when_configured_exclusion_rule_is_not_found(self,
                                                                                               mock_config_loader: ConfigLoader):
        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=['invalid-rule-name']))

        entry = Mock()

        with self.assertRaises(EntryExclusionRuleNotFoundException) as context:
            ExclusionFilter(mock_config_loader).should_exclude_entry(entry)

        self.assertIn('invalid-rule-name', str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(ExclusionRules)

    @patch(fully_qualified_property_name(ExclusionFilter, '_EXCLUSION_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_should_exclude_entry_raises_exception_when_exclusion_rule_raises_exception(self,
                                                                                        mock_config_loader: ConfigLoader,
                                                                                        mock_rules: MagicMock):

        mock_config_loader.read_config = MagicMock(return_value=Mock(rules=[_RULE_NAME]))
        mock_rule = MagicMock(side_effect=Exception())
        mock_rules.return_value = {_RULE_NAME: mock_rule}

        entry = Mock()
        with self.assertRaises(ExclusionRuleFailedException) as context:
            ExclusionFilter(mock_config_loader).should_exclude_entry(entry)

        self.assertIn(_RULE_NAME, str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(ExclusionRules)
