from __future__ import annotations

from typing import TYPE_CHECKING

from app.schema import Token

if TYPE_CHECKING:
    from app.runtime import LoxObject


class LoxError(BaseException): ...


class LoxParserError(LoxError): ...


class LoxRuntimeError(LoxError):
    token: Token
    message: str

    def __init__(self, token: Token, message: str) -> None:
        super().__init__(message)
        self.token = token
        self.message = message


class LoxException(BaseException): ...


class LoxFlowException(LoxException):
    token: Token

    def __init__(self, token: Token) -> None:
        self.token = token


class LoxLoopException(LoxFlowException): ...


class LoxReturnException(LoxFlowException):
    value: LoxObject

    def __init__(self, token: Token, value: LoxObject) -> None:
        super().__init__(token)
        self.value = value
