from collections.abc import Sequence
from typing import Any
from app import util
from app.environment import Environment
from app.errors import InterpreterError
from app.expression import (
    AssignExpr,
    BinaryExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    TernaryExpr,
    UnaryExpr,
    ExprVisitor,
    VariableExpr,
)
from app.logger import Logger
from app.schema import Token, TokenType
from app.statement import ExpressionStmt, PrintStmt, Stmt, StmtVisitor, VarStmt


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
    _environment: Environment

    def __init__(self, _logger: Logger):
        self._logger = _logger
        self._environment = Environment()

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

    def visit_binary_expr(self, expr: BinaryExpr) -> Any:
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

    def visit_grouping_expr(self, expr: GroupingExpr) -> Any:
        return self._evaluate(expr.expr)

    def visit_literal_expr(self, expr: LiteralExpr) -> Any:
        return expr.value

    def visit_unary_expr(self, expr: UnaryExpr) -> Any:
        value = self._evaluate(expr.expr)

        match (expr.operator.type_):
            case TokenType.MINUS:
                _check_number_operand(expr.operator, value)
                return -1 * value
            case TokenType.BANG:
                return not util.is_truthy(value)

        return None

    def visit_ternary_expr(self, expr: TernaryExpr) -> Any:
        condition = self._evaluate(expr.condition)

        if util.is_truthy(condition):
            return self._evaluate(expr.true_expr)

        return self._evaluate(expr.false_expr)

    def visit_variable_expr(self, expr: VariableExpr) -> Any:
        return self._environment.get(expr.name)

    def visit_assign_expr(self, expr: AssignExpr) -> Any:
        value = self._evaluate(expr.value_expr)
        self._environment.assign(expr.name, value)
        return value

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._evaluate(stmt.expr)

    def visit_print_stmt(self, stmt: PrintStmt) -> None:
        value = self._evaluate(stmt.expr)
        print(util.stringify(value))

    def visit_var_stmt(self, stmt: VarStmt) -> None:
        value = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self._environment.define(stmt.name, value)
