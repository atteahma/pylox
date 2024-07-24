from app.schema import Token


class LoxError(BaseException): ...


class LoxParserError(LoxError): ...


class LoxRuntimeError(LoxError):
    token: Token
    message: str

    def __init__(self, _token: Token, _message: str) -> None:
        super().__init__(_message)
        self.token = _token
        self.message = _message


class LoxException(BaseException): ...


class LoxFlowException(LoxException):
    token: Token

    def __init__(self, _token: Token) -> None:
        self.token = _token
