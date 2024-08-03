from typing import List, Any


def make_lowercase(values: List[str]) -> List[str]:
    """
    Make all the strings in the list lowercase.

    :param values: The list of strings to make lowercase.
    :return: A new list with all the strings entirely in lowercase.
    """
    return [value.lower() for value in values]


def make_debug_string(value: Any) -> str:
    """
    Converts the input value into a loggable string. The string will contain the name of the type,
    the name of all the public (non-callable) properties, and the values associated with each property.

    An example string may look like the following:
    DebugProperties(enable_trace_logs=True, log_file='debug.log')

    :param value: The value to be converted into a loggable string. This value cannot be None.
    :return: A string representation of the input value.
    """

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
