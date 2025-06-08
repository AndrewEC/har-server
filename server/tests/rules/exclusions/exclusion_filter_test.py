import unittest
from unittest.mock import Mock, patch, PropertyMock

from server.core.config import ConfigLoader
from server.core.config.models import ExclusionRules
from server.core.rules.exclusions import ExclusionFilter
from server.core.rules.base import RuleFailedException

from server.tests.util import fully_qualified_name, fully_qualified_property_name


_RULE_NAME = 'test-rule'


class ExclusionFilterTest(unittest.TestCase):

    @patch(fully_qualified_property_name(ExclusionFilter, '_EXCLUSION_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_should_exclude_entry(self,
                                  mock_config_loader: ConfigLoader,
                                  mock_rules: Mock):

        for result in [True, False]:
            with self.subTest(should_filter=result):
                mock_rule = Mock(
                    get_name=Mock(return_value=_RULE_NAME),
                    should_filter_out=Mock(return_value=result)
                )
                mock_rules.return_value = [Mock(return_value=mock_rule)]

                mock_config_loader.read_config = Mock(return_value=Mock(rules=[_RULE_NAME]))

                entry = Mock()
                actual = ExclusionFilter(mock_config_loader).should_exclude_entry(entry)
                self.assertEqual(result, actual)

                mock_config_loader.read_config.assert_called_once_with(ExclusionRules)
                mock_rule.should_filter_out.assert_called_once_with(entry)

    @patch(fully_qualified_property_name(ExclusionFilter, '_EXCLUSION_RULES'), new_callable=PropertyMock)
    @patch(fully_qualified_name(ConfigLoader))
    def test_should_exclude_entry_raises_exception_when_exclusion_rule_raises_exception(self,
                                                                                        mock_config_loader: ConfigLoader,
                                                                                        mock_rules: Mock):

        mock_config_loader.read_config = Mock(return_value=Mock(rules=[_RULE_NAME]))
        mock_rule = Mock(
            get_name=Mock(return_value=_RULE_NAME),
            should_filter_out=Mock(side_effect=Exception())
        )
        mock_rules.return_value = [Mock(return_value=mock_rule)]

        entry = Mock()
        with self.assertRaises(RuleFailedException) as context:
            ExclusionFilter(mock_config_loader).should_exclude_entry(entry)

        self.assertIn(_RULE_NAME, str(context.exception))

        mock_config_loader.read_config.assert_called_once_with(ExclusionRules)
        mock_rule.should_filter_out.assert_called_once_with(entry)
