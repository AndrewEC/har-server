from typing import Type, Callable, Any
from abc import ABC


_POST_CONSTRUCT_PROPERTY = '__post_construct_name__'


class InvalidPostConstructMethod(Exception, ABC):

    _MESSAGE_TEMPLATE = '{} Method [{}] was configured on type [{}]'

    def __init__(self, sub_message: str, name: str, configurable: Any):
        super().__init__(InvalidPostConstructMethod._MESSAGE_TEMPLATE.format(sub_message, name, type(configurable).__name__))


class MissingPostConstructMethod(InvalidPostConstructMethod):

    _SUB_MESSAGE = 'A post_construct method could not be found.'

    def __init__(self, name: str, configurable: Any):
        super().__init__(MissingPostConstructMethod._SUB_MESSAGE, name, configurable)


class NonCallablePostConstructMethod(InvalidPostConstructMethod):

    _SUB_MESSAGE = 'A post_construct method was found but is not callable. It may not be a method.'

    def __init__(self, name, configurable: Any):
        super().__init__(NonCallablePostConstructMethod._SUB_MESSAGE, name, configurable)


def post_construct(name: str) -> Callable:
    def wrap(cls: Type) -> Type:
        setattr(cls, _POST_CONSTRUCT_PROPERTY, name)
        return cls
    return wrap


def _get_post_construct_name(cls: Type) -> str | None:
    if not hasattr(cls, _POST_CONSTRUCT_PROPERTY):
        return None
    return getattr(cls, _POST_CONSTRUCT_PROPERTY)


def invoke_post_construct(instance: Any):
    method_name = _get_post_construct_name(instance)
    if method_name is None:
        return

    if not hasattr(instance, method_name):
        raise MissingPostConstructMethod(method_name, instance)

    post_construct_method = getattr(instance, method_name)

    if not callable(post_construct_method):
        raise NonCallablePostConstructMethod(method_name, instance)

    post_construct_method()
