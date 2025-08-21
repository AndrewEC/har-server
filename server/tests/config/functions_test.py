import unittest

from server.core.config.functions import make_lowercase


class FunctionsTests(unittest.TestCase):

    def test_make_lowercase(self):
        items = ['FIRST', 'Second', 'third']
        expected = ['first', 'second', 'third']

        actual = make_lowercase(items)

        self.assertEqual(expected, actual)
