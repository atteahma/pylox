from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from app.runtime import LoxObject
from app.schema import AstNode, Token

# All AstNode dataclasses are @dataclass(frozen=True, eq=False)
# Because we want to inherit __hash__ from AstNode

R = TypeVar("R", covariant=True)


class Visitor(Generic[R], ABC):
    @abstractmethod
    def visit_binary_expr(self, expr: Binary) -> R: ...

    @abstractmethod
    def visit_grouping_expr(self, expr: Grouping) -> R: ...

    @abstractmethod
    def visit_literal_expr(self, expr: Literal) -> R: ...

    @abstractmethod
    def visit_unary_expr(self, expr: Unary) -> R: ...

    @abstractmethod
    def visit_ternary_expr(self, expr: Ternary) -> R: ...

    @abstractmethod
    def visit_variable_expr(self, expr: Variable) -> R: ...

    @abstractmethod
    def visit_assign_expr(self, expr: Assign) -> R: ...

    @abstractmethod
    def visit_logical_expr(self, expr: Logical) -> R: ...

    @abstractmethod
    def visit_call_expr(self, expr: Call) -> R: ...

    @abstractmethod
    def visit_get_expr(self, expr: Get) -> R: ...

    @abstractmethod
    def visit_set_expr(self, expr: Set) -> R: ...

    @abstractmethod
    def visit_this_expr(self, expr: This) -> R: ...

    @abstractmethod
    def visit_super_expr(self, expr: Super) -> R: ...


class Expr(AstNode):
    @abstractmethod
    def accept(self, visitor: Visitor[R]) -> R: ...


@dataclass(frozen=True, eq=False)
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_binary_expr(self)


@dataclass(frozen=True, eq=False)
class Ternary(Expr):
    condition: Expr
    true_expr: Expr
    false_expr: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_ternary_expr(self)


@dataclass(frozen=True, eq=False)
class Grouping(Expr):
    expr: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_grouping_expr(self)


@dataclass(frozen=True, eq=False)
class Literal(Expr):
    value: LoxObject

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_literal_expr(self)


@dataclass(frozen=True, eq=False)
class Unary(Expr):
    operator: Token
    expr: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_unary_expr(self)


@dataclass(frozen=True, eq=False)
class Variable(Expr):
    name: Token

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_variable_expr(self)


@dataclass(frozen=True, eq=False)
class Assign(Expr):
    name: Token
    value_expr: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_assign_expr(self)


@dataclass(frozen=True, eq=False)
class Logical(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_logical_expr(self)


@dataclass(frozen=True, eq=False)
class Call(Expr):
    callee: Expr
    paren: Token
    arguments: list[Expr]

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_call_expr(self)


@dataclass(frozen=True, eq=False)
class Get(Expr):
    object: Expr
    name: Token

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_get_expr(self)


@dataclass(frozen=True, eq=False)
class Set(Expr):
    object: Expr
    name: Token
    value: Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_set_expr(self)


@dataclass(frozen=True, eq=False)
class This(Expr):
    keyword: Token

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_this_expr(self)


@dataclass(frozen=True, eq=False)
class Super(Expr):
    keyword: Token
    method: Token

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_super_expr(self)
