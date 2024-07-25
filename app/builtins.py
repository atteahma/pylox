from __future__ import annotations
from collections.abc import Sequence
import time
from typing import TYPE_CHECKING

from app.schema import LoxCallable, LoxObject

if TYPE_CHECKING:
    from app.interpreter import Interpreter


class Clock(LoxCallable):
    def arity(self) -> int:
        return 0

    def call(self, _: Interpreter, arguments: Sequence[LoxObject]) -> float:
        return time.time()

    def __str__(self) -> str:
        return "<native fn 'clock'>"
