from typing import Any


def fully_qualified_name(cls: Any) -> str:
    return cls.__module__ + '.' + cls.__name__


def fully_qualified_property_name(cls: Any, property_name: str) -> str:
    return fully_qualified_name(cls) + '.' + property_name
