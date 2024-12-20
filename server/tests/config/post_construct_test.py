import unittest

from server.core.config.post_construct import _get_post_construct_name, post_construct


_POST_CONSTRUCT_NAME = 'post_construct_name'


@post_construct(_POST_CONSTRUCT_NAME)
class _TestModel:
    pass


class _TestModel2:
    pass


class PostConstructTests(unittest.TestCase):

    def test_get_post_construct_name(self):
        actual = _get_post_construct_name(_TestModel)
        self.assertEqual(_POST_CONSTRUCT_NAME, actual)

        self.assertIsNone(_get_post_construct_name(_TestModel2))

