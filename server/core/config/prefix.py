from typing import Any, Callable, Type


_PREFIX_ATTRIBUTE = '__property_path_prefix__'


class NotPrefixedException(Exception):

    _MESSAGE_TEMPLATE = ('The class [{}] does not have any property prefix to retrieve. '
                         'Configuration classes must be decorated with @prefix.')

    def __init__(self, cls: Any):
        super().__init__(NotPrefixedException._MESSAGE_TEMPLATE.format(type(cls).__name__))


def prefix(path: str) -> Callable:
    def wrap(cls: Any) -> Any:
        setattr(cls, _PREFIX_ATTRIBUTE, path)
        return cls
    return wrap


def get_prefix(cls: Type):
    if not hasattr(cls, _PREFIX_ATTRIBUTE):
        raise NotPrefixedException(cls)
    return getattr(cls, _PREFIX_ATTRIBUTE)
