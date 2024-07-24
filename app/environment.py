from typing import Any

from app.errors import InterpreterError
from app.schema import Token


class Environment:
    _values: dict[str, Any] = {}

    def __init__(self) -> None:
        self._values = {}

    def define(self, name: Token, value: Any) -> None:
        lexeme = name.lexeme
        self._values[lexeme] = value

    def get(self, name: Token) -> Any:
        lexeme = name.lexeme

        if lexeme not in self._values:
            raise InterpreterError(name, "Undefined variable '" + lexeme + "'.")

        return self._values[lexeme]

    def assign(self, name: Token, value: Any) -> None:
        lexeme = name.lexeme

        if lexeme not in self._values:
            raise InterpreterError(name, "Undefined variable '" + lexeme + "'.")

        self._values[lexeme] = value
