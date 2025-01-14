import unittest
from unittest.mock import Mock, patch

from pydantic import BaseModel

from server.core.config import prefix, ConfigLoader, ConfigParser, post_construct

from server.tests.util import fully_qualified_name


_DEFAULT_VALUE = 'default_value'
_NON_DEFAULT_VALUE = 'non_default_value'


@prefix('prefix')
class _TestModel(BaseModel):
    string: str = _DEFAULT_VALUE


@post_construct('post_construct')
@prefix('prefix')
class _TestModelWithPostConstruct(BaseModel):
    string: str = _DEFAULT_VALUE
    called: bool = False

    def post_construct(self):
        self.called = True


class _InvalidTestModel:
    pass


class LoaderTests(unittest.TestCase):

    @patch(fully_qualified_name(ConfigParser))
    def test_read_config(self, mock_config_parser: ConfigParser):
        mock_config_parser.parse_config_yml = Mock(return_value={'prefix': {'string': _NON_DEFAULT_VALUE}})

        actual = ConfigLoader(mock_config_parser).read_config(_TestModel)

        self.assertEqual(_NON_DEFAULT_VALUE, actual.string)
        mock_config_parser.parse_config_yml.assert_called_once()

    @patch(fully_qualified_name(ConfigParser))
    def test_read_config_with_post_construct(self, mock_config_parser: ConfigParser):
        mock_config_parser.parse_config_yml = Mock(return_value={'prefix': {'string': _NON_DEFAULT_VALUE}})

        actual = ConfigLoader(mock_config_parser).read_config(_TestModelWithPostConstruct)

        self.assertEqual(_NON_DEFAULT_VALUE, actual.string)
        self.assertTrue(actual.called)
        mock_config_parser.parse_config_yml.assert_called_once()

    @patch(fully_qualified_name(ConfigParser))
    def test_read_config_returns_default_when_property_not_found_in_config(self, mock_config_parser: ConfigParser):
        mock_config_parser.parse_config_yml = Mock(return_value={})

        actual = ConfigLoader(mock_config_parser).read_config(_TestModel)

        self.assertEqual(_DEFAULT_VALUE, actual.string)
        mock_config_parser.parse_config_yml.assert_called_once()
