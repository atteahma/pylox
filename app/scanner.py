from typing import Any
from app.logger import Logger
from app.schema import Token, TokenType
from app import util

KEYWORDS: dict[str, TokenType] = {
    "and": TokenType.AND,
    "class": TokenType.CLASS,
    "else": TokenType.ELSE,
    "false": TokenType.FALSE,
    "for": TokenType.FOR,
    "fun": TokenType.FUN,
    "if": TokenType.IF,
    "nil": TokenType.NIL,
    "or": TokenType.OR,
    "print": TokenType.PRINT,
    "return": TokenType.RETURN,
    "super": TokenType.SUPER,
    "this": TokenType.THIS,
    "true": TokenType.TRUE,
    "var": TokenType.VAR,
    "while": TokenType.WHILE,
}


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

    def _is_at_end(self, *, offset: int = 0) -> bool:
        index = self._current + offset
        return index >= len(self._source)

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

    def _peek(self, *, offset: int = 0) -> str:
        if self._is_at_end(offset=offset):
            return "\0"

        index = self._current + offset
        return self._source[index]

    def _add_token(self, type_: TokenType, literal: Any = None) -> None:
        text = self._source[self._start : self._current]
        token = Token(type_, text, literal, self._line)
        self._tokens.append(token)

    def _string(self) -> None:
        while not self._is_at_end() and self._peek() != '"':
            if self._peek() == "\n":
                self._line += 1
            self._advance()

        if self._is_at_end():
            self._logger.log_error(self._line, "Unterminated string.")
            return

        # Advance past closing "
        self._advance()

        start_i = self._start + 1
        end_i = self._current - 1
        value = self._source[start_i:end_i]
        self._add_token(TokenType.STRING, value)

    def _number(self) -> None:
        def advance_while_digit():
            while util.is_digit(self._peek()):
                self._advance()

        advance_while_digit()

        # Handle decimal values
        if self._peek() == "." and util.is_digit(self._peek(offset=1)):
            self._advance()

            advance_while_digit()

        value_str = self._source[self._start : self._current]
        value = float(value_str)
        self._add_token(TokenType.NUMBER, value)

    def _identifier(self) -> None:
        while util.is_alphanumeric(self._peek(), underscore_allowed=True):
            self._advance()

        text = self._source[self._start : self._current]
        type_ = KEYWORDS.get(text) or TokenType.IDENTIFIER
        self._add_token(type_)

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
                # Advance until the end of the line
                while self._peek() != "\n" and not self._is_at_end():
                    self._advance()
            case "/":
                self._add_token(TokenType.SLASH)
            case " " | "\r" | "\t":
                # Ignore whitespace
                pass
            case "\n":
                # Ignore newline, but increment line number
                self._line += 1
            case '"':
                self._string()
            case _ if util.is_digit(char):
                self._number()
            case _ if util.is_alpha(char, underscore_allowed=True):
                self._identifier()
            case _:
                self._logger.log_error(self._line, f"Unexpected character: {char}")
