from typing import List, Any


def make_lowercase(values: List[str]) -> List[str]:
    return [value.lower() for value in values]


def make_debug_string(value: Any) -> str:
    type_name = type(value).__name__
    fields = []
    for field in dir(value):
        if field[0] == '_':  # Skip private fields.
            continue
        field_value = getattr(value, field)
        if callable(field_value):  # Skip functions.
            continue
        fields.append(field)
    property_string = ', '.join(f'{field}={getattr(value, field)}' for field in fields)
    return f'{type_name}({property_string})'
