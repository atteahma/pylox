from __future__ import annotations

from collections.abc import Callable, Sequence
import time
import random
from typing import TYPE_CHECKING

from app.errors import LoxRuntimeError
from app.runtime import LoxCallable, LoxObject
from app.schema import Token

if TYPE_CHECKING:
    from app.interpreter import Interpreter


class Clock(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(
        self, _: Interpreter, arguments: Sequence[LoxObject], token: Token
    ) -> float:
        return time.time()

    def __str__(self) -> str:
        return "<native fn 'clock'>"


class RandInt(LoxCallable):
    def arity(self) -> int:
        return 2

    def call(self, _: Interpreter, arguments: Sequence[LoxObject], token: Token) -> int:
        left = arguments[0]
        right = arguments[1]

        if not isinstance(left, float) or not isinstance(right, float):
            raise LoxRuntimeError(token, "Arguments to randInt must be numbers.")

        return random.randint(int(left), int(right))

    def __str__(self) -> str:
        return "<native fn 'randInt'>"


class Random(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(
        self, _: Interpreter, arguments: Sequence[LoxObject], token: Token
    ) -> float:
        return random.random()

    def __str__(self) -> str:
        return "<native fn 'random'>"


BUILTINS: dict[str, Callable] = {
    "clock": Clock,
    "randInt": RandInt,
    "random": Random,
}
