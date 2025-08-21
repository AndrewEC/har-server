from typing import List


def make_lowercase(values: List[str]) -> List[str]:
    """
    Make all the strings in the list lowercase.

    :param values: The list of strings to make lowercase.
    :return: A new list with all the strings entirely in lowercase.
    """
    return [value.lower() for value in values]
