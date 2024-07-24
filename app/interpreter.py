from collections.abc import Sequence
from typing import Any
from app import util
from app.errors import InterpreterError
from app.expression import (
    BinaryExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    TernaryExpr,
    UnaryExpr,
    ExprVisitor,
)
from app.logger import Logger
from app.schema import Token, TokenType
from app.statement import ExpressionStmt, PrintStmt, Stmt, StmtVisitor


def _check_number_operand(token: Token, operand: Any) -> None:
    if type(operand) is float:
        return

    raise InterpreterError(token, f"Operand to {token.lexeme} must be a number.")


def _check_number_operands(token: Token, left: Any, right: Any) -> None:
    if type(left) is float and type(right) is float:
        return

    raise InterpreterError(token, f"Operands to {token.lexeme} must be numbers.")


def _check_number_or_string_operands(token: Token, left: Any, right: Any) -> None:
    if type(left) is float and type(right) is float:
        return
    if type(left) is str and type(right) is str:
        return

    raise InterpreterError(
        token, f"Operands to {token.lexeme} must be numbers or strings."
    )


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
    _logger: Logger

    def __init__(self, _logger: Logger):
        self._logger = _logger

    def interpret(self, statements: Sequence[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except InterpreterError as err:
            self._logger.report_runtime(err)

    def _execute(self, statement: Stmt) -> None:
        statement.accept(self)

    def _evaluate(self, expression: Expr) -> Any:
        return expression.accept(self)

    def visitBinaryExpr(self, expr: BinaryExpr) -> Any:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        match (expr.operator.type_):
            case TokenType.MINUS:
                _check_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.STAR:
                _check_number_operands(expr.operator, left, right)
                return left * right
            case TokenType.SLASH:
                _check_number_operands(expr.operator, left, right)
                return left / right
            case TokenType.PLUS:
                _check_number_or_string_operands(expr.operator, left, right)
                return left + right
            case TokenType.LESS:
                _check_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                _check_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.GREATER:
                _check_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                _check_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.BANG_EQUAL:
                return not util.is_equal(left, right)
            case TokenType.EQUAL:
                return util.is_equal(left, right)

        return None

    def visitGroupingExpr(self, expr: GroupingExpr) -> Any:
        return self._evaluate(expr.expr)

    def visitLiteralExpr(self, expr: LiteralExpr) -> Any:
        return expr.value

    def visitUnaryExpr(self, expr: UnaryExpr) -> Any:
        value = self._evaluate(expr.expr)

        match (expr.operator.type_):
            case TokenType.MINUS:
                _check_number_operand(expr.operator, value)
                return -1 * value
            case TokenType.BANG:
                return not util.is_truthy(value)

        return None

    def visitTernaryExpr(self, expr: TernaryExpr) -> Any:
        condition = self._evaluate(expr.condition)

        if util.is_truthy(condition):
            return self._evaluate(expr.true_expr)

        return self._evaluate(expr.false_expr)

    def visitExpressionStmt(self, stmt: ExpressionStmt) -> None:
        self._evaluate(stmt.expr)

    def visitPrintStmt(self, stmt: PrintStmt) -> None:
        value = self._evaluate(stmt.expr)
        print(util.stringify(value))
