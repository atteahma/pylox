from app.errors import LoxRuntimeError
from app.schema import Token
from app.runtime import LoxObject


def number_operand(token: Token, operand: LoxObject) -> float:
    if isinstance(operand, float):
        return operand

    raise LoxRuntimeError(token, f"Operand to {token.lexeme} must be a number.")


def number_operands(
    token: Token, left: LoxObject, right: LoxObject
) -> tuple[float, float]:
    if isinstance(left, float) and isinstance(right, float):
        return left, right

    raise LoxRuntimeError(token, f"Operands to {token.lexeme} must be numbers.")


def number_or_string_operands(
    token: Token, left: LoxObject, right: LoxObject
) -> tuple[float, float] | tuple[str, str]:
    if isinstance(left, float) and isinstance(right, float):
        return left, right
    if isinstance(left, str) and isinstance(right, str):
        return left, right

    raise LoxRuntimeError(
        token, f"Operands to {token.lexeme} must be numbers or strings."
    )
