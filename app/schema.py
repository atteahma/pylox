from dataclasses import dataclass
from enum import StrEnum, auto
from typing import Any, Generic, TypeVar


class TokenType(StrEnum):
    # Single-character tokens.
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    LEFT_BRACE = auto()
    RIGHT_BRACE = auto()

    COMMA = auto()
    DOT = auto()
    MINUS = auto()
    PLUS = auto()
    SEMICOLON = auto()
    SLASH = auto()
    STAR = auto()

    QUESTION = auto()
    COLON = auto()

    # One or two character tokens.
    BANG = auto()
    BANG_EQUAL = auto()

    EQUAL = auto()
    EQUAL_EQUAL = auto()

    GREATER = auto()
    GREATER_EQUAL = auto()

    LESS = auto()
    LESS_EQUAL = auto()

    # Literals.
    IDENTIFIER = auto()
    STRING = auto()
    NUMBER = auto()

    # Keywords.
    AND = auto()
    CLASS = auto()
    ELSE = auto()
    FALSE = auto()
    FUN = auto()
    FOR = auto()
    IF = auto()
    NIL = auto()
    OR = auto()

    PRINT = auto()
    RETURN = auto()
    SUPER = auto()
    THIS = auto()
    TRUE = auto()
    VAR = auto()
    WHILE = auto()

    EOF = auto()


@dataclass
class Token:
    type_: TokenType
    lexeme: str
    literal: Any
    line: int

    def __repr__(self) -> str:
        literal_str = "null" if self.literal is None else self.literal
        return f"{self.type_.upper()} {self.lexeme} {literal_str}"


ResultValue = TypeVar("ResultValue")


class Result(Generic[ResultValue]):
    def __init__(self, value: ResultValue, had_error: bool) -> None:
        self.value = value
        self.had_error = had_error


class Command(StrEnum):
    TOKENIZE = auto()
    PARSE = auto()
    INTERPRET = auto()
