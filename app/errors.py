from app.schema import Token


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
