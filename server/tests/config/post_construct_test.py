import unittest

from server.core.config.post_construct import (
    post_construct,
    invoke_post_construct,
    MissingPostConstructMethod,
    NonCallablePostConstructMethod
)


_POST_CONSTRUCT_NAME = 'post_construct_name'


@post_construct(_POST_CONSTRUCT_NAME)
class _ValidTestModel:

    def __init__(self):
        self.invoked = False

    def post_construct_name(self):
        self.invoked = True


@post_construct(_POST_CONSTRUCT_NAME)
class _ModelWithMissingMethod:
    pass


@post_construct(_POST_CONSTRUCT_NAME)
class _ModelWithPropertySpecifiedAsPostConstructMethod:

    def __init__(self):
        self.post_construct_name = None


class PostConstructTests(unittest.TestCase):

    def test_invoke_post_construct(self):
        instance = _ValidTestModel()
        invoke_post_construct(instance)
        self.assertTrue(instance.invoked)

    def test_invoke_post_construct_with_missing_method_throws_exception(self):
        instance = _ModelWithMissingMethod()
        self.assertRaises(MissingPostConstructMethod, lambda: invoke_post_construct(instance))

    def test_invoke_post_construct_with_non_callable_definition_throws_exception(self):
        instance = _ModelWithPropertySpecifiedAsPostConstructMethod()
        self.assertRaises(NonCallablePostConstructMethod, lambda: invoke_post_construct(instance))
