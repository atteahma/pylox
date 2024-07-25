from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

from app.statement import FunctionStmt


if TYPE_CHECKING:
    from app.interpreter import Interpreter


class LoxCallable(ABC):
    @abstractmethod
    def arity(self) -> int: ...

    @abstractmethod
    def call(
        self, interpreter: Interpreter, arguments: Sequence[LoxObject]
    ) -> LoxObject: ...

    @abstractmethod
    def __str__(self) -> str: ...


LoxObject = LoxCallable | float | str | bool | None


class LoxFunction(LoxCallable):
    _declaration: FunctionStmt

    def __init__(self, declaration: FunctionStmt) -> None:
        self._declaration = declaration
