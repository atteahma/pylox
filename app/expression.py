from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Generic, TypeVar

from app.schema import Token


R = TypeVar("R", covariant=True)


class ExprVisitor(Generic[R], ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: "BinaryExpr") -> R: ...

    @abstractmethod
    def visit_grouping_expr(self, expr: "GroupingExpr") -> R: ...

    @abstractmethod
    def visit_literal_expr(self, expr: "LiteralExpr") -> R: ...

    @abstractmethod
    def visit_unary_expr(self, expr: "UnaryExpr") -> R: ...

    @abstractmethod
    def visit_ternary_expr(self, expr: "TernaryExpr") -> R: ...

    @abstractmethod
    def visit_variable_expr(self, expr: "VariableExpr") -> R: ...


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: ExprVisitor[R]) -> R: ...


@dataclass
class BinaryExpr(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_binary_expr(self)


@dataclass
class TernaryExpr(Expr):
    condition: Expr
    true_expr: Expr
    false_expr: Expr

    def accept(self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_ternary_expr(self)


@dataclass
class GroupingExpr(Expr):
    expr: Expr

    def accept(self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_grouping_expr(self)


@dataclass
class LiteralExpr(Expr):
    value: Any

    def accept(self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_literal_expr(self)


@dataclass
class UnaryExpr(Expr):
    operator: Token
    expr: Expr

    def accept(self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_unary_expr(self)


@dataclass
class VariableExpr(Expr):
    name: Token

    def accept(self, visitor: ExprVisitor[R]) -> R:
        return visitor.visit_variable_expr(self)
