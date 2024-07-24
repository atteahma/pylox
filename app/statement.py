from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Generic, TypeVar

from app.expression import Expr

R = TypeVar("R", covariant=True)


class StmtVisitor(Generic[R], ABC):
    @abstractmethod
    def visitExprStmt(self, stmt: "ExprStmt") -> R: ...

    @abstractmethod
    def visitPrintStmt(self, expr: "PrintStmt") -> R: ...


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: StmtVisitor[R]) -> R: ...


@dataclass
class ExprStmt(Stmt):
    expr: Expr

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visitExprStmt(self)


@dataclass
class PrintStmt(Stmt):
    expr: Expr

    def accept(self, visitor: StmtVisitor[R]) -> R:
        return visitor.visitPrintStmt(self)
