import unittest

from server.core.config.prefix import get_prefix, prefix


_PREFIX_NAME = 'prefix_name'


@prefix(_PREFIX_NAME)
class _TestModel:
    pass


class _TestModel2:
    pass


class PrefixTests(unittest.TestCase):

    def test_get_prefix(self):
        self.assertEqual(_PREFIX_NAME, get_prefix(_TestModel))
        self.assertIsNone(get_prefix(_TestModel2))
