import sys

from app.schema import Token, TokenType


class Logger:
    had_error: bool

    def __init__(self) -> None:
        self.had_error = False

    def _log(self, line: int, where: str, message: str) -> None:
        log_str = f"[line {line}] Error{where}: {message}"
        print(log_str, file=sys.stderr)

    def scanner_error(self, line: int, message: str) -> None:
        self.had_error = True
        self._log(line, "", message)

    def parser_error(self, token: Token, message: str) -> None:
        self.had_error = True
        if token.type_ == TokenType.EOF:
            self._log(token.line, " at end", message)
        else:
            self._log(token.line, " at '" + token.lexeme + "'", message)
