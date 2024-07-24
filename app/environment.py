from typing import Any

from app.errors import InterpreterError
from app.schema import Token


class Environment:
    _values: dict[str, Any] = {}
    _enclosing: "Environment | None"

    def __init__(self, enclosing: "Environment | None" = None) -> None:
        self._values = {}
        self._enclosing = enclosing

    def define(self, name: Token, value: Any) -> None:
        lexeme = name.lexeme
        self._values[lexeme] = value

    def get(self, name: Token) -> Any:
        lexeme = name.lexeme

        if lexeme in self._values:
            return self._values[lexeme]

        if self._enclosing is not None:
            return self._enclosing.get(name)

        raise InterpreterError(name, "Undefined variable '" + lexeme + "'.")

    def assign(self, name: Token, value: Any) -> None:
        lexeme = name.lexeme

        if lexeme in self._values:
            self._values[lexeme] = value
            return

        if self._enclosing is not None:
            self._enclosing.assign(name, value)
            return

        raise InterpreterError(name, "Undefined variable '" + lexeme + "'.")
