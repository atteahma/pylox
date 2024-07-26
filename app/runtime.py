from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import TYPE_CHECKING

from app.constants import CONSTRUCTOR_METHOD_NAME, THIS_KEYWORD
from app.environment import Environment
from app.errors import LoxReturnException, LoxRuntimeError
from app.schema import Token

if TYPE_CHECKING:
    from app.interpreter import Interpreter
    from app import statement as Stmt


class LoxCallable(ABC):
    @abstractmethod
    def call(
        self, interpreter: Interpreter, arguments: Sequence[LoxObject], token: Token
    ) -> LoxObject: ...

    @abstractmethod
    def arity(self) -> int: ...

    @abstractmethod
    def __str__(self) -> str: ...


class LoxInstance:
    class_: LoxClass
    fields_: dict[str, LoxObject]

    def __init__(self, class_: LoxClass) -> None:
        self.class_ = class_
        self.fields_ = {}

    def __str__(self) -> str:
        return f"{self.class_.name} instance"

    def get(self, name: Token) -> LoxObject:
        if name.lexeme in self.fields_:
            return self.fields_[name.lexeme]

        method = self.class_.find_method(name.lexeme)
        if method is not None:
            return method.bind(self)

        raise LoxRuntimeError(name, f"Undefined property '{name.lexeme}'.")

    def set(self, name: Token, value: LoxObject) -> None:
        self.fields_[name.lexeme] = value


LoxObject = LoxInstance | LoxCallable | float | str | bool | None


class LoxFunction(LoxCallable):
    _declaration: Stmt.Function
    _closure: Environment
    _is_initializer: bool

    def __init__(
        self, declaration: Stmt.Function, closure: Environment, is_initializer: bool
    ) -> None:
        self._declaration = declaration
        self._closure = closure
        self._is_initializer = is_initializer

    def bind(self, instance: LoxInstance) -> LoxFunction:
        environment = Environment(self._closure)
        environment.define(THIS_KEYWORD, instance)
        return LoxFunction(self._declaration, environment, self._is_initializer)

    def call(
        self, interpreter: Interpreter, arguments: Sequence[LoxObject], token: Token
    ) -> LoxObject:
        parameters = self._declaration.params
        body = self._declaration.body

        environment = Environment(self._closure)
        for parameter, argument in zip(parameters, arguments):
            environment.define(parameter.lexeme, argument)

        try:
            interpreter.execute_block(body, environment)
        except LoxReturnException as ret:
            if self._is_initializer:
                return self._closure.get_at(0, THIS_KEYWORD)

            return ret.value

        if self._is_initializer:
            return self._closure.get_at(0, THIS_KEYWORD)

        return None

    def arity(self) -> int:
        return len(self._declaration.params)

    def __str__(self) -> str:
        return f"<fn {self._declaration.name.lexeme}>"


class LoxClass(LoxCallable):
    name: str
    superclass: LoxClass | None
    _methods: dict[str, LoxFunction]

    def __init__(
        self, name: str, superclass: LoxClass | None, methods: dict[str, LoxFunction]
    ) -> None:
        self.name = name
        self.superclass = superclass
        self._methods = methods

    def call(
        self, interpreter: Interpreter, arguments: Sequence[LoxObject], token: Token
    ) -> LoxObject:
        instance = LoxInstance(self)

        initializer = self.find_method(CONSTRUCTOR_METHOD_NAME)
        if initializer is not None:
            initializer.bind(instance).call(interpreter, arguments, token)

        return instance

    def arity(self) -> int:
        initializer = self.find_method(CONSTRUCTOR_METHOD_NAME)
        if initializer is not None:
            return initializer.arity()

        return 0

    def __str__(self) -> str:
        return self.name

    def find_method(self, name: str) -> LoxFunction | None:
        if name in self._methods:
            return self._methods[name]

        if self.superclass is not None:
            return self.superclass.find_method(name)

        return None
