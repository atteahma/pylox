from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

from app.environment import Environment
from app.errors import LoxReturnException

if TYPE_CHECKING:
    from app.interpreter import Interpreter
    from app.statement import FunctionStmt


class LoxCallable(ABC):
    @abstractmethod
    def call(
        self, interpreter: Interpreter, arguments: Sequence[LoxObject]
    ) -> LoxObject: ...

    @abstractmethod
    def arity(self) -> int: ...

    @abstractmethod
    def __str__(self) -> str: ...


LoxObject = LoxCallable | float | str | bool | None


class LoxFunction(LoxCallable):
    _declaration: FunctionStmt

    def __init__(self, declaration: FunctionStmt) -> None:
        self._declaration = declaration

    def call(
        self, interpreter: Interpreter, arguments: Sequence[LoxObject]
    ) -> LoxObject:
        parameters = self._declaration.params
        body = self._declaration.body

        environment = Environment(interpreter.globals)
        for parameter, argument in zip(parameters, arguments):
            environment.define(parameter.lexeme, argument)

        try:
            interpreter.execute_block(body, environment)
        except LoxReturnException as ret:
            return ret.value

        return None

    def arity(self) -> int:
        return len(self._declaration.params)

    def __str__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}>"
