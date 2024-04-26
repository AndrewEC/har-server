from typing import Dict


def are_dictionaries_equal(first: Dict[str, str], second: Dict[str, str]) -> bool:
    if len(first) != len(second):
        return False

    for first_key in first.keys():
        if first_key not in second or first[first_key] != second[first_key]:
            return False

    return True
