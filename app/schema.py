from __future__ import annotations

from abc import ABC
from dataclasses import dataclass
from enum import StrEnum, auto
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from app.runtime import LoxObject


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
    BREAK = auto()
    CONTINUE = auto()

    EOF = auto()


@dataclass(frozen=True)
class Token:
    type_: TokenType
    lexeme: str
    literal: LoxObject
    line: int

    def __repr__(self) -> str:
        literal_str = "null" if self.literal is None else self.literal
        return f"{self.type_.upper()} {self.lexeme} {literal_str} {self.line}"


ResultValue = TypeVar("ResultValue")


class Result(Generic[ResultValue]):
    def __init__(self, value: ResultValue, had_error: bool) -> None:
        self.value = value
        self.had_error = had_error


class Command(StrEnum):
    TOKENIZE = auto()
    PARSE = auto()
    INTERPRET = auto()


class OpMode(StrEnum):
    REPL = auto()
    PROGRAM = auto()


class FunctionType(StrEnum):
    FUNCTION = auto()
    METHOD = auto()
    INITIALIZER = auto()


class ClassType(StrEnum):
    CLASS = auto()


class AstNode(ABC):
    def __hash__(self) -> int:
        return id(self)
