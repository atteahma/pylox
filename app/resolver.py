from collections.abc import Sequence
from app.errors import LoxResolverError
from app.expression import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    Expr,
    ExprVisitor,
    GetExpr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    SetExpr,
    TernaryExpr,
    ThisExpr,
    UnaryExpr,
    VariableExpr,
)
from app.interpreter import Interpreter
from app.logger import Logger
from app.schema import FunctionType, Token, TokenType
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


class Resolver(ExprVisitor[None], StmtVisitor[None]):
    _logger: Logger
    _interpreter: Interpreter
    _scopes: list[dict[str, bool]]  # python lists have O(1) stack operations
    _current_function: FunctionType | None

    def __init__(self, logger: Logger, interpreter: Interpreter):
        self._logger = logger
        self._interpreter = interpreter
        self._scopes = []
        self._current_function = None

    def resolve(self, statements: Sequence[Stmt]) -> None:
        for statement in statements:
            self._resolve(statement)

    def _resolve(self, thing: Expr | Stmt) -> None:
        thing.accept(self)

    def _begin_scope(self) -> None:
        self._scopes.append({})

    def _end_scope(self) -> None:
        self._scopes.pop()

    def _declare(self, name: Token) -> None:
        if len(self._scopes) == 0:
            return

        scope = self._scopes[-1]

        if name.lexeme in scope:
            self._error(name, "Already a variable with this name in this scope.")

        scope[name.lexeme] = False

    def _define(self, name: Token) -> None:
        if len(self._scopes) == 0:
            return

        scope = self._scopes[-1]
        scope[name.lexeme] = True

    def _error(self, token: Token, message: str) -> LoxResolverError:
        where = "end" if token.type_ == TokenType.EOF else f"'{token.lexeme}'"
        self._logger.report(token.line, f" at {where}", message)

        return LoxResolverError()

    def _resolve_local(self, expr: Expr, name: Token) -> None:
        for i_from_end, scope in enumerate(reversed(self._scopes)):
            if name.lexeme in scope:
                self._interpreter.resolve(expr, i_from_end)
                return

    def _resolve_function(self, function: FunctionStmt, type_: FunctionType) -> None:
        enclosing_function = self._current_function
        self._current_function = type_

        self._begin_scope()
        for param in function.params:
            self._declare(param)
            self._define(param)

        self.resolve(function.body)
        self._end_scope()

        self._current_function = enclosing_function

    def visit_block_stmt(self, stmt: BlockStmt) -> None:
        self._begin_scope()
        self.resolve(stmt.statements)
        self._end_scope()

    def visit_var_stmt(self, stmt: VarStmt) -> None:
        self._declare(stmt.name)
        if stmt.initializer is not None:
            self._resolve(stmt.initializer)
        self._define(stmt.name)

    def visit_variable_expr(self, expr: VariableExpr) -> None:
        scope = self._scopes[-1] if self._scopes else None

        if scope is not None and scope.get(expr.name.lexeme) is False:
            self._error(expr.name, "Cannot read local variable in its own initializer.")

        self._resolve_local(expr, expr.name)

    def visit_assign_expr(self, expr: AssignExpr) -> None:
        self._resolve(expr.value_expr)
        self._resolve_local(expr, expr.name)

    def visit_function_stmt(self, stmt: FunctionStmt) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)

        self._resolve_function(stmt, FunctionType.FUNCTION)

    def visit_expression_stmt(self, stmt: ExpressionStmt) -> None:
        self._resolve(stmt.expr)

    def visit_if_stmt(self, stmt: IfStmt) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.then_stmt)
        if stmt.else_stmt is not None:
            self._resolve(stmt.else_stmt)

    def visit_print_stmt(self, stmt: PrintStmt) -> None:
        self._resolve(stmt.expr)

    def visit_return_stmt(self, stmt: ReturnStmt) -> None:
        if self._current_function is None:
            self._error(stmt.keyword, "Can't return from top-level code.")

        if stmt.value is not None:
            self._resolve(stmt.value)

    def visit_while_stmt(self, stmt: WhileStmt) -> None:
        self._resolve(stmt.condition)
        self._resolve(stmt.body)

    def visit_binary_expr(self, expr: BinaryExpr) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_call_expr(self, expr: CallExpr) -> None:
        self._resolve(expr.callee)
        for argument in expr.arguments:
            self._resolve(argument)

    def visit_grouping_expr(self, expr: GroupingExpr) -> None:
        self._resolve(expr.expr)

    def visit_literal_expr(self, expr: LiteralExpr) -> None:
        pass

    def visit_logical_expr(self, expr: LogicalExpr) -> None:
        self._resolve(expr.left)
        self._resolve(expr.right)

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        self._resolve(expr.expr)

    def visit_flow_stmt(self, stmt: FlowStmt) -> None:
        pass

    def visit_ternary_expr(self, expr: TernaryExpr) -> None:
        raise NotImplementedError("Resolver.visit_ternary_expr not implemented")

    def visit_class_stmt(self, stmt: ClassStmt) -> None:
        self._declare(stmt.name)
        self._define(stmt.name)

        self._begin_scope()
        self._scopes[-1]["this"] = True

        for method in stmt.methods:
            declaration = FunctionType.METHOD
            if method.name.lexeme == "init":
                declaration = FunctionType.INITIALIZER

            self._resolve_function(method, declaration)

        self._end_scope()

    def visit_get_expr(self, expr: GetExpr) -> None:
        self._resolve(expr.object)

    def visit_set_expr(self, expr: SetExpr) -> None:
        self._resolve(expr.value)
        self._resolve(expr.object)

    def visit_this_expr(self, expr: ThisExpr) -> None:
        self._resolve_local(expr, expr.keyword)
