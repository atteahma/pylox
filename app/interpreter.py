from collections.abc import Sequence
from typing import Protocol, cast
from app import util
from app.environment import Environment
from app.errors import LoxFlowException, LoxRuntimeError
from app.expression import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    TernaryExpr,
    UnaryExpr,
    ExprVisitor,
    VariableExpr,
)
from app.logger import Logger
from app.schema import LoxCallable, LoxObject, Token, TokenType
from app.statement import (
    BlockStmt,
    ExpressionStmt,
    FlowStmt,
    IfStmt,
    PrintStmt,
    Stmt,
    StmtVisitor,
    VarStmt,
    WhileStmt,
)


def _validate_number_operand(token: Token, operand: LoxObject) -> float:
    if isinstance(operand, float):
        return operand

    raise LoxRuntimeError(token, f"Operand to {token.lexeme} must be a number.")


def _validate_number_operands(
    token: Token, left: LoxObject, right: LoxObject
) -> tuple[float, float]:
    if isinstance(left, float) and isinstance(right, float):
        return left, right

    raise LoxRuntimeError(token, f"Operands to {token.lexeme} must be numbers.")


def _validate_number_or_string_operands(
    token: Token, left: LoxObject, right: LoxObject
) -> tuple[float, float] | tuple[str, str]:
    if isinstance(left, float) and isinstance(right, float):
        return left, right
    if isinstance(left, str) and isinstance(right, str):
        return left, right

    raise LoxRuntimeError(
        token, f"Operands to {token.lexeme} must be numbers or strings."
    )


class Interpreter(ExprVisitor[LoxObject], StmtVisitor[None]):
    _logger: Logger
    _environment: Environment

    def __init__(self, _logger: Logger):
        self._logger = _logger
        self._environment = Environment()

    def interpret(self, statements: Sequence[Stmt]) -> None:
        try:
            try:
                for statement in statements:
                    self._execute(statement)
            except LoxFlowException as exc:
                raise LoxRuntimeError(exc.token, "Flow statement used outside loop.")
        except LoxRuntimeError as err:
            self._logger.report_runtime(err)

    def _execute(self, statement: Stmt) -> None:
        statement.accept(self)

    def _execute_block(
        self, statements: Sequence[Stmt], environment: Environment
    ) -> None:
        previous = self._environment

        try:
            self._environment = environment

            for statement in statements:
                self._execute(statement)
        finally:
            self._environment = previous

    def _evaluate(self, expression: Expr) -> LoxObject:
        return expression.accept(self)

    def visit_binary_expr(self, expr: BinaryExpr) -> LoxObject:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        match (expr.operator.type_):
            case TokenType.MINUS:
                left, right = _validate_number_operands(expr.operator, left, right)
                return left - right
            case TokenType.STAR:
                left, right = _validate_number_operands(expr.operator, left, right)
                return left * right
            case TokenType.SLASH:
                left, right = _validate_number_operands(expr.operator, left, right)
                return left / right
            case TokenType.PLUS:
                left_right = _validate_number_or_string_operands(
                    expr.operator, left, right
                )
                return util.add(*left_right)
            case TokenType.LESS:
                left, right = _validate_number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                left, right = _validate_number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.GREATER:
                left, right = _validate_number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                left, right = _validate_number_operands(expr.operator, left, right)
                return left >= right
            case TokenType.BANG_EQUAL:
                return not util.is_equal(left, right)
            case TokenType.EQUAL:
                return util.is_equal(left, right)

        return None

    def visit_grouping_expr(self, expr: GroupingExpr) -> LoxObject:
        return self._evaluate(expr.expr)

    def visit_literal_expr(self, expr: LiteralExpr) -> LoxObject:
        return expr.value

    def visit_unary_expr(self, expr: UnaryExpr) -> LoxObject:
        value = self._evaluate(expr.expr)

        match (expr.operator.type_):
            case TokenType.MINUS:
                value = _validate_number_operand(expr.operator, value)
                return -1 * value
            case TokenType.BANG:
                return not util.is_truthy(value)

        return None

    def visit_ternary_expr(self, expr: TernaryExpr) -> LoxObject:
        condition = self._evaluate(expr.condition)

        if util.is_truthy(condition):
            return self._evaluate(expr.true_expr)

        return self._evaluate(expr.false_expr)

    def visit_variable_expr(self, expr: VariableExpr) -> LoxObject:
        return self._environment.get(expr.name)

    def visit_assign_expr(self, expr: AssignExpr) -> LoxObject:
        value = self._evaluate(expr.value_expr)
        self._environment.assign(expr.name, value)
        return value

    def visit_logical_expr(self, expr: LogicalExpr) -> LoxObject:
        left = self._evaluate(expr.left)

        if expr.operator.type_ == TokenType.OR and util.is_truthy(left):
            return left
        if expr.operator.type_ == TokenType.AND and not util.is_truthy(left):
            return left

        return self._evaluate(expr.right)

    def visit_call_expr(self, expr: CallExpr) -> LoxObject:
        func = self._evaluate(expr.callee)
        arguments = [self._evaluate(arg) for arg in expr.arguments]

        if not isinstance(func, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        return func.call(self, arguments)

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

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        environment = Environment(enclosing=self._environment)
        self._execute_block(stmt.statements, environment)

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        condition = self._evaluate(stmt.condition)

        if util.is_truthy(condition):
            self._execute(stmt.then_stmt)
        elif stmt.else_stmt is not None:
            self._execute(stmt.else_stmt)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        while util.is_truthy(self._evaluate(stmt.condition)):
            try:
                self._execute(stmt.body)
            except LoxFlowException as exc:
                if exc.token.type_ == TokenType.BREAK:
                    break
                elif exc.token.type_ == TokenType.CONTINUE:
                    continue

                raise exc

    def visit_flow_stmt(self, stmt: FlowStmt) -> None:
        raise LoxFlowException(stmt.token)
