from collections.abc import Sequence
import sys
from app import builtins, util
from app.environment import Environment
from app.errors import LoxLoopException, LoxReturnException, LoxRuntimeError
from app.expression import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    Expr,
    GetExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    SetExpr,
    TernaryExpr,
    UnaryExpr,
    ExprVisitor,
    VariableExpr,
)
from app.logger import Logger
from app.schema import OpMode, Token, TokenType
from app.runtime import LoxCallable, LoxClass, LoxFunction, LoxInstance, LoxObject
from app.statement import (
    BlockStmt,
    ClassStmt,
    ExpressionStmt,
    FlowStmt,
    FunctionStmt,
    IfStmt,
    PrintStmt,
    ReturnStmt,
    Stmt,
    StmtVisitor,
    VarStmt,
    WhileStmt,
)
from app import validate


class Interpreter(ExprVisitor[LoxObject], StmtVisitor[None]):
    globals: Environment

    _logger: Logger
    _environment: Environment
    _op_mode: OpMode
    _locals: dict[Expr, int]

    def __init__(self, logger: Logger, op_mode: OpMode):
        self._logger = logger
        self._op_mode = op_mode

        self.globals = Environment()
        self._environment = self.globals

        self._locals = {}

        self.globals.define("clock", builtins.Clock())

    def interpret(self, statements: Sequence[Stmt]) -> None:
        try:
            try:
                for statement in statements:
                    self._execute_mode(statement)
            except LoxLoopException as exc:
                raise LoxRuntimeError(exc.token, "Flow statement used outside loop.")
        except LoxRuntimeError as err:
            self._logger.report_runtime(err)

    def _execute_mode(self, statement: Stmt) -> None:
        if self._op_mode == OpMode.REPL and isinstance(statement, ExpressionStmt):
            value = self._evaluate(statement.expr)
            print(util.stringify(value), file=sys.stdout)
            return

        self._execute(statement)

    def _execute(self, statement: Stmt) -> None:
        statement.accept(self)

    def execute_block(
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

    def resolve(self, expr: Expr, depth: int) -> None:
        self._locals[expr] = depth

    def _look_up_variable(self, name: Token, expr: VariableExpr) -> LoxObject:
        distance = self._locals.get(expr)

        if distance is None:
            return self.globals.get(name)

        return self._environment.get_at(distance, name.lexeme)

    def visit_binary_expr(self, expr: BinaryExpr) -> LoxObject:
        left = self._evaluate(expr.left)
        right = self._evaluate(expr.right)

        match (expr.operator.type_):
            case TokenType.MINUS:
                left, right = validate.number_operands(expr.operator, left, right)
                return left - right
            case TokenType.STAR:
                left, right = validate.number_operands(expr.operator, left, right)
                return left * right
            case TokenType.SLASH:
                left, right = validate.number_operands(expr.operator, left, right)
                return left / right
            case TokenType.PLUS:
                left_right = validate.number_or_string_operands(
                    expr.operator, left, right
                )
                return util.add(*left_right)
            case TokenType.LESS:
                left, right = validate.number_operands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                left, right = validate.number_operands(expr.operator, left, right)
                return left <= right
            case TokenType.GREATER:
                left, right = validate.number_operands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                left, right = validate.number_operands(expr.operator, left, right)
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
                value = validate.number_operand(expr.operator, value)
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
        return self._look_up_variable(expr.name, expr)

    def visit_assign_expr(self, expr: AssignExpr) -> LoxObject:
        value = self._evaluate(expr.value_expr)

        distance = self._locals.get(expr)
        if distance is None:
            self.globals.assign(expr.name, value)
        else:
            self._environment.assign_at(distance, expr.name, value)

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

        if func.arity() != len(arguments):
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {func.arity()} arguments but got {len(arguments)}.",
            )

        return func.call(self, arguments)

    def visit_get_expr(self, expr: GetExpr) -> LoxObject:
        object_ = self._evaluate(expr.object)
        if not isinstance(object_, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have properties.")

        return object_.get(expr.name)

    def visit_set_expr(self, expr: SetExpr) -> LoxObject:
        object_ = self._evaluate(expr.object)
        if not isinstance(object_, LoxInstance):
            raise LoxRuntimeError(expr.name, "Only instances have fields.")

        value = self._evaluate(expr.value)
        object_.set(expr.name, value)

        return value

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._evaluate(stmt.expr)

    def visit_print_stmt(self, stmt: PrintStmt) -> None:
        value = self._evaluate(stmt.expr)
        print(util.stringify(value), file=sys.stdout)

    def visit_var_stmt(self, stmt: VarStmt) -> None:
        value = None
        if stmt.initializer is not None:
            value = self._evaluate(stmt.initializer)

        self._environment.define(stmt.name.lexeme, value)

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        environment = Environment(enclosing=self._environment)
        self.execute_block(stmt.statements, environment)

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
            except LoxLoopException as exc:
                if exc.token.type_ == TokenType.BREAK:
                    break
                elif exc.token.type_ == TokenType.CONTINUE:
                    continue

                raise exc

    def visit_flow_stmt(self, stmt: FlowStmt) -> None:
        raise LoxLoopException(stmt.token)

    def visit_function_stmt(self, stmt: FunctionStmt) -> None:
        func = LoxFunction(stmt, self._environment)
        self._environment.define(stmt.name.lexeme, func)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        value: LoxObject = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)

        raise LoxReturnException(stmt.keyword, value)

    def visit_class_stmt(self, stmt: ClassStmt) -> None:
        self._environment.define(stmt.name.lexeme, None)

        methods = {}
        for method in stmt.methods:
            func = LoxFunction(method, self._environment)
            methods[method.name.lexeme] = func

        class_ = LoxClass(stmt.name.lexeme, methods)
        self._environment.assign(stmt.name, class_)
