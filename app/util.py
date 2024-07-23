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
