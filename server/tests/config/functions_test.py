import unittest

from server.core.config.functions import make_lowercase, make_debug_string


class _TestModel:

    def __init__(self):
        self.first = 'first_property'
        self._second = 'second_property'

    def method(self) -> str:
        return 'method'


class FunctionsTests(unittest.TestCase):

    def test_make_lowercase(self):
        items = ['FIRST', 'Second', 'third']
        expected = ['first', 'second', 'third']

        actual = make_lowercase(items)

        self.assertEqual(expected, actual)

    def test_make_debug_string(self):
        expected = '_TestModel(first=first_property)'

        actual = make_debug_string(_TestModel())

        self.assertEqual(expected, actual)
