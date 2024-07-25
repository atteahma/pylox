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

    def get_level_and_assert(self, name: str) -> LoxObject:
        assert name in self._values, "Variable not found on get -- resolver mismatch."
        return self._values[name]

    def get_at(self, distance: int, name: str) -> LoxObject:
        environment = self._ancestor(distance)
        return environment.get_level_and_assert(name)

    def assign(self, name: Token, value: LoxObject) -> None:
        lexeme = name.lexeme

        if lexeme in self._values:
            self._values[lexeme] = value
            return

        if self._enclosing is not None:
            self._enclosing.assign(name, value)
            return

        raise LoxRuntimeError(name, "Undefined variable '" + lexeme + "'.")

    def assign_level_and_assert(self, name: Token, value: LoxObject) -> None:
        assert (
            name.lexeme in self._values
        ), "Variable not found on assign -- resolver mismatch."
        self._values[name.lexeme] = value

    def assign_at(self, distance: int, name: Token, value: LoxObject) -> None:
        environment = self._ancestor(distance)
        environment.assign_level_and_assert(name, value)

    def _ancestor(self, distance: int) -> Environment:
        environment = self
        for _ in range(distance):
            assert (
                environment._enclosing is not None
            ), "Environment not found -- resolver mismatch."
            environment = environment._enclosing

        return environment
