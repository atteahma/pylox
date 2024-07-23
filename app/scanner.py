from typing import Any
from app.logger import Logger
from app.schema import Token, TokenType


class Scanner:
    _logger: Logger

    _source: str
    _tokens: list[Token]
    _start: int
    _current: int
    _line: int

    def __init__(self, _logger: Logger, _source: str) -> None:
        self._logger = _logger

        self._source = _source
        self._tokens = []
        self._start = 0
        self._current = 0
        self._line = 1

    def scan_tokens(self) -> list[Token]:
        while not self._is_at_end():
            # We are at the beginning of the next lexeme.
            self._start = self._current
            self._scan_token()

        self._start = self._current
        self._add_token(TokenType.EOF)

        return self._tokens

    def _is_at_end(self) -> bool:
        return self._current >= len(self._source)

    def _advance(self) -> str:
        char = self._source[self._current]
        self._current += 1
        return char

    def _match(self, expected: str) -> bool:
        if self._is_at_end():
            return False
        if self._source[self._current] != expected:
            return False

        self._current += 1
        return True

    def _peek(self) -> str:
        if self._is_at_end():
            return "\0"

        return self._source[self._current]

    def _add_token(self, type_: TokenType, literal: Any = None) -> None:
        text = self._source[self._start : self._current]
        token = Token(type_, text, literal, self._line)
        self._tokens.append(token)

    def _scan_token(self) -> None:
        char = self._advance()

        match (char):
            case "(":
                self._add_token(TokenType.LEFT_PAREN)
            case ")":
                self._add_token(TokenType.RIGHT_PAREN)
            case "{":
                self._add_token(TokenType.LEFT_BRACE)
            case "}":
                self._add_token(TokenType.RIGHT_BRACE)
            case ",":
                self._add_token(TokenType.COMMA)
            case ".":
                self._add_token(TokenType.DOT)
            case "-":
                self._add_token(TokenType.MINUS)
            case "+":
                self._add_token(TokenType.PLUS)
            case ";":
                self._add_token(TokenType.SEMICOLON)
            case "*":
                self._add_token(TokenType.STAR)
            case "=" if self._match("="):
                self._add_token(TokenType.EQUAL_EQUAL)
            case "=":
                self._add_token(TokenType.EQUAL)
            case "!" if self._match("="):
                self._add_token(TokenType.BANG_EQUAL)
            case "!":
                self._add_token(TokenType.BANG)
            case "<" if self._match("="):
                self._add_token(TokenType.LESS_EQUAL)
            case "<":
                self._add_token(TokenType.LESS)
            case ">" if self._match("="):
                self._add_token(TokenType.GREATER_EQUAL)
            case ">":
                self._add_token(TokenType.GREATER)
            case "/" if self._match("/"):
                # A comment goes until the end of the line.
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
            case "/":
                self._add_token(TokenType.SLASH)
            case _:
                self._logger.log_error(self._line, f"Unexpected character: {char}")
