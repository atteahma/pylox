from typing import Any


def is_alpha(char: str, *, underscore_allowed: bool = False) -> bool:
    if char.isalnum():
        return True
    if underscore_allowed and char == "_":
        return True

    return False


def is_digit(char: str, *, decimal_allowed: bool = False) -> bool:
    if char.isdigit():
        return True
    if decimal_allowed and char == ".":
        return True

    return False


def is_alphanumeric(
    char: str, *, decimal_allowed: bool = False, underscore_allowed: bool = False
) -> bool:
    if is_alpha(char, underscore_allowed=underscore_allowed):
        return True
    if is_digit(char, decimal_allowed=decimal_allowed):
        return True

    return False


def is_truthy(value: Any) -> bool:
    if value is None:
        return False
    if type(value) is bool:
        return value

    return True


def is_equal(a: Any, b: Any) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False

    return a == b


def stringify(value: Any, double_to_int: bool = True) -> str:
    if value is None:
        return "nil"
    if value is True:
        return "true"
    if value is False:
        return "false"

    str_value = str(value)

    if double_to_int and type(value) is float and str_value.endswith(".0"):
        str_value = str_value.removesuffix(".0")

    return str_value
