from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from app import expression as Expr
from app.schema import AstNode, Token

# All AstNode dataclasses are @dataclass(frozen=True, eq=False)
# Because we want to inherit __hash__ from AstNode

R = TypeVar("R", covariant=True)


class Visitor(Generic[R], ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt: Expression) -> R: ...

    @abstractmethod
    def visit_print_stmt(self, stmt: Print) -> R: ...

    @abstractmethod
    def visit_var_stmt(self, stmt: Var) -> R: ...

    @abstractmethod
    def visit_block_stmt(self, stmt: Block) -> R: ...

    @abstractmethod
    def visit_if_stmt(self, stmt: If) -> R: ...

    @abstractmethod
    def visit_while_stmt(self, stmt: While) -> R: ...

    @abstractmethod
    def visit_flow_stmt(self, stmt: Flow) -> R: ...

    @abstractmethod
    def visit_function_stmt(self, stmt: Function) -> R: ...

    @abstractmethod
    def visit_return_stmt(self, stmt: Return) -> R: ...

    @abstractmethod
    def visit_class_stmt(self, stmt: Class) -> R: ...


class Stmt(AstNode):
    @abstractmethod
    def accept(self, visitor: Visitor[R]) -> R: ...


@dataclass(frozen=True, eq=False)
class Expression(Stmt):
    expr: Expr.Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_expression_stmt(self)


@dataclass(frozen=True, eq=False)
class Print(Stmt):
    expr: Expr.Expr

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_print_stmt(self)


@dataclass(frozen=True, eq=False)
class Var(Stmt):
    name: Token
    initializer: Expr.Expr | None

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_var_stmt(self)


@dataclass(frozen=True, eq=False)
class Block(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_block_stmt(self)


@dataclass(frozen=True, eq=False)
class If(Stmt):
    condition: Expr.Expr
    then_stmt: Stmt
    else_stmt: Stmt | None

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_if_stmt(self)


@dataclass(frozen=True, eq=False)
class While(Stmt):
    condition: Expr.Expr
    body: Stmt

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_while_stmt(self)


@dataclass(frozen=True, eq=False)
class Flow(Stmt):
    token: Token

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_flow_stmt(self)


@dataclass(frozen=True, eq=False)
class Function(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_function_stmt(self)


@dataclass(frozen=True, eq=False)
class Return(Stmt):
    keyword: Token
    value: Expr.Expr | None

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_return_stmt(self)


@dataclass(frozen=True, eq=False)
class Class(Stmt):
    name: Token
    superclass: Expr.Variable | None
    methods: list[Function]

    def accept(self, visitor: Visitor[R]) -> R:
        return visitor.visit_class_stmt(self)
