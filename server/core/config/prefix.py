from typing import Any, Callable, Type, TypeVar

from pydantic import BaseModel


_T = TypeVar('_T', bound=BaseModel)

_PREFIX_ATTRIBUTE = '__property_path_prefix__'


class InvalidPropertyException(Exception):

    _MESSAGE_TEMPLATE = 'Type [{}] does not have requested property [{}]'

    def __init__(self, cls: Type, property_name: str):
        super().__init__(InvalidPropertyException._MESSAGE_TEMPLATE.format(cls, property_name))


class NotPrefixedException(Exception):

    _MESSAGE_TEMPLATE = ('The class [{}] does not have any property prefix to retrieve. '
                         'Configuration classes must be decorated with @prefix.')

    def __init__(self, cls: Any):
        super().__init__(NotPrefixedException._MESSAGE_TEMPLATE.format(type(cls).__name__))


def prefix(path: str) -> Callable:
    """
    Adds a __property_path_prefix__ property the decorated type with the value
    equal to the input path.

    :param path: The partial path to the property.
    :return: The original decorated type with the prefix path property.
    """
    def wrap(cls: Any) -> Any:
        setattr(cls, _PREFIX_ATTRIBUTE, path)
        return cls
    return wrap


def get_prefix(cls: Type) -> str | None:
    """
    Returns the value of the __property_path_prefix__ property if said property
    is present on the input type, otherwise None.

    :param cls: The input type to read the __property_path_prefix__ value from.
    :return: The value of __property_path_prefix__ or None if said property is not defined.
    """
    if not hasattr(cls, _PREFIX_ATTRIBUTE):
        return None
    return getattr(cls, _PREFIX_ATTRIBUTE)


def get_prop_config_path(cls: Type[_T], property_name: str) -> str:
    """
    Gets the full path to the property. The full path is a combination of the
    return value of get_prefix plus the property name.

    This requires the input type, cls, to be decorated with @prefix. If the input
    type is not then this will raise a NotPrefixedException.

    :param cls: The prefixed type.
    :param property_name: The name of the property to get the config path to.
    :return: The path to the property.
    :raises NotPrefixedException: Raised if the input type, cls, is not decorated
        with @prefix.
    """
    prefix_value = get_prefix(cls)
    if prefix_value is None:
        raise NotPrefixedException(cls)

    if not any(property_name == field for field in cls.model_fields):
        raise InvalidPropertyException(cls, property_name)

    config_prop_name = property_name.replace('_', '-')
    return f'{prefix_value}.{config_prop_name}'
