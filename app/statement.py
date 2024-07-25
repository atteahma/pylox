from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from app.expression import Expr
from app.schema import Token

R = TypeVar("R", covariant=True)


class StmtVisitor(Generic[R], ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt: ExpressionStmt) -> R: ...

    @abstractmethod
    def visit_print_stmt(self, stmt: PrintStmt) -> R: ...

    @abstractmethod
    def visit_var_stmt(self, stmt: VarStmt) -> R: ...

    @abstractmethod
    def visit_block_stmt(self, stmt: BlockStmt) -> R: ...

    @abstractmethod
    def visit_if_stmt(self, stmt: IfStmt) -> R: ...

    @abstractmethod
    def visit_while_stmt(self, stmt: WhileStmt) -> R: ...

    @abstractmethod
    def visit_flow_stmt(self, stmt: FlowStmt) -> R: ...

    @abstractmethod
    def visit_function_stmt(self, stmt: FunctionStmt) -> R: ...

    @abstractmethod
    def visit_return_stmt(self, stmt: ReturnStmt) -> R: ...


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor[R]) -> R: ...


@dataclass
class ExpressionStmt(Stmt):
    expr: Expr

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_expression_stmt(self)


@dataclass
class PrintStmt(Stmt):
    expr: Expr

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_print_stmt(self)


@dataclass
class VarStmt(Stmt):
    name: Token
    initializer: Expr | None

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_var_stmt(self)


@dataclass
class BlockStmt(Stmt):
    statements: list[Stmt]

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_block_stmt(self)


@dataclass
class IfStmt(Stmt):
    condition: Expr
    then_stmt: Stmt
    else_stmt: Stmt | None

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_if_stmt(self)


@dataclass
class WhileStmt(Stmt):
    condition: Expr
    body: Stmt

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_while_stmt(self)


@dataclass
class FlowStmt(Stmt):
    token: Token

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_flow_stmt(self)


@dataclass
class FunctionStmt(Stmt):
    name: Token
    params: list[Token]
    body: list[Stmt]

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_function_stmt(self)


@dataclass
class ReturnStmt(Stmt):
    keyword: Token
    value: Expr | None

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_return_stmt(self)
