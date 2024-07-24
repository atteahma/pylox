from app.schema import Token


class CustomError(BaseException): ...


class ParserError(CustomError): ...


class InterpreterError(CustomError):
    token: Token
    message: str

    def __init__(self, _token: Token, _message: str) -> None:
        super().__init__(_message)
        self.token = _token
        self.message = _message


class FlowException(BaseException):
    token: Token

    def __init__(self, _token: Token) -> None:
        self.token = _token
