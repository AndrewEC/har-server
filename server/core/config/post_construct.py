from typing import Type, Callable, Any


_POST_CONSTRUCT_PROPERTY = '__post_construct_name__'


class MissingPostConstructMethod(Exception):

    _MESSAGE_TEMPLATE = ('A post_construct method of name [{}] was configured on type [{}] but no method with that '
                         'name could be found on that type.')

    def __init__(self, name: str, configurable: Any):
        super().__init__(MissingPostConstructMethod._MESSAGE_TEMPLATE.format(name, type(configurable).__name__))


def post_construct(name: str) -> Callable:
    def wrap(cls: Type) -> Type:
        setattr(cls, _POST_CONSTRUCT_PROPERTY, name)
        return cls
    return wrap


def get_post_construct_name(cls: Type) -> str | None:
    if not hasattr(cls, _POST_CONSTRUCT_PROPERTY):
        return None
    return getattr(cls, _POST_CONSTRUCT_PROPERTY)
