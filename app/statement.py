from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from app.expression import Expr
from app.schema import Token

R = TypeVar("R", covariant=True)


class StmtVisitor(Generic[R], ABC):
    @abstractmethod
    def visit_expression_stmt(self, stmt: "ExpressionStmt") -> R: ...

    @abstractmethod
    def visit_print_stmt(self, stmt: "PrintStmt") -> R: ...

    @abstractmethod
    def visit_var_stmt(self, stmt: "VarStmt") -> R: ...


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
    expr: Expr | None

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visit_var_stmt(self)
