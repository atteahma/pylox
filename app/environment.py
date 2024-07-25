from __future__ import annotations

from typing import TYPE_CHECKING

from app.errors import LoxRuntimeError
from app.schema import Token

if TYPE_CHECKING:
    from app.runtime import LoxObject


class Environment:
    _values: dict[str, LoxObject]
    _enclosing: Environment | None

    def __init__(self, enclosing: Environment | None = None) -> None:
        self._values = {}
        self._enclosing = enclosing

    def define(self, name: str, value: LoxObject) -> None:
        self._values[name] = value

    def get(self, name: Token) -> LoxObject:
        lexeme = name.lexeme

        if lexeme in self._values:
            return self._values[lexeme]

        if self._enclosing is not None:
            return self._enclosing.get(name)

        raise LoxRuntimeError(name, "Undefined variable '" + lexeme + "'.")

    def assign(self, name: Token, value: LoxObject) -> None:
        lexeme = name.lexeme

        if lexeme in self._values:
            self._values[lexeme] = value
            return

        if self._enclosing is not None:
            self._enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, "Undefined variable '" + lexeme + "'.")
