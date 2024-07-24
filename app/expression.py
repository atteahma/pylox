from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from app.schema import Token


R = TypeVar("R", covariant=True)


class Visitor(Generic[R], ABC):
    @abstractmethod
    def visitBinaryExpr(self, expr: "BinaryExpr") -> R: ...

    @abstractmethod
    def visitGroupingExpr(self, expr: "GroupingExpr") -> R: ...

    @abstractmethod
    def visitLiteralExpr(self, expr: "LiteralExpr") -> R: ...

    @abstractmethod
    def visitUnaryExpr(self, expr: "UnaryExpr") -> R: ...


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: Visitor[R]) -> R: ...


@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visitBinaryExpr(self)


@dataclass
class GroupingExpr(Expr):
    expr: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visitGroupingExpr(self)


@dataclass
class LiteralExpr(Expr):
    value: Any

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visitLiteralExpr(self)


@dataclass
class UnaryExpr(Expr):
    operator: Token
    expr: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visitUnaryExpr(self)
