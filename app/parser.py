from collections.abc import Sequence
from app.errors import LoxParserError
from app.expression import (
    AssignExpr,
    BinaryExpr,
    CallExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    LogicalExpr,
    UnaryExpr,
    VariableExpr,
)
from app.logger import Logger
from app.schema import FunctionType, Token, TokenType
from app.statement import (
    BlockStmt,
    ExpressionStmt,
    FlowStmt,
    FunctionStmt,
    IfStmt,
    PrintStmt,
    Stmt,
    VarStmt,
    WhileStmt,
)

MAX_ARG_COUNT = 255


class Parser:
    _logger: Logger
    _tokens: list[Token]
    _current: int

    def __init__(self, logger: Logger, tokens: Sequence[Token]) -> None:
        self._logger = logger

        self._tokens = list(tokens)
        self._current = 0

    def parse(self) -> list[Stmt]:
        statements = []

        while not self._is_at_end():
            statement = self._declaration()

            if statement is not None:
                statements.append(statement)

        return statements

    def parse_expression(self) -> Expr | None:
        try:
            return self._expression()
        except LoxParserError:
            pass

        return None

    def _peek(self, *, offset: int = 0) -> Token:
        index = self._current + offset
        return self._tokens[index]

    def _is_at_end(self) -> bool:
        return self._peek().type_ == TokenType.EOF

    def _advance(self) -> Token:
        value = self._peek()
        if not self._is_at_end():
            self._current += 1

        return value

    def _check(self, type_: TokenType) -> bool:
        if self._is_at_end():
            return False

        return self._peek().type_ == type_

    def _match(self, *types: TokenType) -> bool:
        for type_ in types:
            if self._check(type_):
                self._advance()
                return True

        return False

    def _consume(self, type_: TokenType, message: str) -> Token:
        if self._check(type_):
            return self._advance()

        raise self._error(
            self._peek(),
            message,
        )

    def _error(self, token: Token, message: str) -> LoxParserError:
        where = "end" if token.type_ == TokenType.EOF else f"'{token.lexeme}'"
        self._logger.report(token.line, f" at {where}", message)

        return LoxParserError()

    def _synchronize(self) -> None:
        self._advance()

        while not self._is_at_end():
            if self._peek(offset=-1).type_ == TokenType.SEMICOLON:
                return

            if self._peek().type_ in (
                TokenType.CLASS,
                TokenType.FUN,
                TokenType.VAR,
                TokenType.FOR,
                TokenType.IF,
                TokenType.WHILE,
                TokenType.PRINT,
                TokenType.RETURN,
            ):
                return

            self._advance()

    def _declaration(self) -> Stmt | None:
        try:
            if self._match(TokenType.VAR):
                return self._var_declaration()
            if self._match(TokenType.FUN):
                return self._function(FunctionType.FUNCTION)

            return self._statement()
        except LoxParserError:
            self._synchronize()
            return None

    def _function(self, type_: FunctionType) -> FunctionStmt:
        name = self._consume(TokenType.IDENTIFIER, f"Expect {type_} name.")
        self._consume(TokenType.LEFT_PAREN, f"Expect '(' after {type_} name.")

        parameters: list[Token] = []
        if self._check(TokenType.IDENTIFIER):
            # collect parameters
            while True:
                if len(parameters) > MAX_ARG_COUNT:
                    _message = f"Can't have more than {MAX_ARG_COUNT} parameters."
                    self._error(self._peek(), _message)

                parameter = self._consume(
                    TokenType.IDENTIFIER, "Expect parameter name."
                )
                parameters.append(parameter)

                if not self._match(TokenType.COMMA):
                    break

        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after parameters.")
        self._consume(TokenType.LEFT_BRACE, f"Expect '{'{'}' before {type_} body.")
        body = self._block()

        return FunctionStmt(name, parameters, body)

    def _statement(self) -> Stmt:
        if self._match(TokenType.IF):
            return self._if_statement()
        if self._match(TokenType.PRINT):
            return self._print_statement()
        if self._match(TokenType.FOR):
            return self._for_statement()
        if self._match(TokenType.WHILE):
            return self._while_statement()
        if self._match(TokenType.LEFT_BRACE):
            return self._block_statement()
        if self._match(TokenType.BREAK, TokenType.CONTINUE):
            return self._flow_statement()

        return self._expression_statement()

    def _flow_statement(self) -> FlowStmt:
        token = self._peek(offset=-1)
        self._consume(TokenType.SEMICOLON, f"Expect ';' after {token.lexeme}")
        return FlowStmt(token)

    def _for_statement(self) -> Stmt:
        def get_initializer() -> Stmt | None:
            if self._match(TokenType.VAR):
                return self._var_declaration()
            elif self._match(TokenType.SEMICOLON):
                return None

            return self._expression_statement()

        def get_condition() -> Expr:
            condition: Expr = LiteralExpr(True)
            if not self._check(TokenType.SEMICOLON):
                condition = self._expression()
            self._consume(TokenType.SEMICOLON, "Expect ';' after loop condition")

            return condition

        def get_increment() -> Expr | None:
            increment = None
            if not self._check(TokenType.RIGHT_PAREN):
                increment = self._expression()

            return increment

        # get parts
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'for'")
        initializer = get_initializer()
        condition = get_condition()
        increment = get_increment()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after for clauses")
        body = self._statement()

        # put together desugared loop
        if increment is not None:
            body = BlockStmt([body, ExpressionStmt(increment)])
        loop: Stmt = WhileStmt(condition, body)
        if initializer is not None:
            loop = BlockStmt([initializer, loop])

        return loop

    def _while_statement(self) -> WhileStmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'while'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")

        body = self._statement()

        return WhileStmt(condition, body)

    def _if_statement(self) -> IfStmt:
        self._consume(TokenType.LEFT_PAREN, "Expect '(' after 'if'.")
        condition = self._expression()
        self._consume(TokenType.RIGHT_PAREN, "Expect ')' after condition.")

        then_stmt = self._statement()

        else_stmt = None
        if self._match(TokenType.ELSE):
            else_stmt = self._statement()

        return IfStmt(condition, then_stmt, else_stmt)

    def _block_statement(self) -> BlockStmt:
        return BlockStmt(self._block())

    def _block(self) -> list[Stmt]:
        statements = []

        while not self._is_at_end() and not self._check(TokenType.RIGHT_BRACE):
            statement = self._declaration()
            if statement is None:
                continue

            statements.append(statement)

        self._consume(TokenType.RIGHT_BRACE, "Expect '}' after block.")

        return statements

    def _var_declaration(self) -> VarStmt:
        name = self._consume(TokenType.IDENTIFIER, "Expect variable name.")

        initializer = None
        if self._match(TokenType.EQUAL):
            initializer = self._expression()

        self._consume(TokenType.SEMICOLON, "Expect ';' after variable declaration.")
        return VarStmt(name, initializer)

    def _print_statement(self) -> PrintStmt:
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after value.")
        return PrintStmt(expr)

    def _expression_statement(self) -> ExpressionStmt:
        expr = self._expression()
        self._consume(TokenType.SEMICOLON, "Expect ';' after expression.")
        return ExpressionStmt(expr)

    def _expression(self) -> Expr:
        return self._assignment()

    def _assignment(self) -> Expr:
        expr = self._or()

        if self._match(TokenType.EQUAL):
            equals = self._peek(offset=-1)
            value = self._assignment()

            if isinstance(expr, VariableExpr):
                name = expr.name
                return AssignExpr(name, value)

            self._error(equals, "Invalid assignment target.")

        return expr

    def _or(self) -> Expr:
        expr = self._and()

        while self._match(TokenType.OR):
            operator = self._peek(offset=-1)
            right = self._and()
            expr = LogicalExpr(expr, operator, right)

        return expr

    def _and(self) -> Expr:
        expr = self._equality()

        while self._match(TokenType.AND):
            operator = self._peek(offset=-1)
            right = self._equality()
            expr = LogicalExpr(expr, operator, right)

        return expr

    def _equality(self) -> Expr:
        expr = self._comparison()

        while self._match(TokenType.BANG_EQUAL, TokenType.EQUAL_EQUAL):
            operator = self._peek(offset=-1)
            right = self._comparison()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _comparison(self) -> Expr:
        expr = self._term()

        while self._match(
            TokenType.GREATER,
            TokenType.GREATER_EQUAL,
            TokenType.LESS,
            TokenType.LESS_EQUAL,
        ):
            operator = self._peek(offset=-1)
            right = self._term()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _term(self) -> Expr:
        expr = self._factor()

        while self._match(TokenType.PLUS, TokenType.MINUS):
            operator = self._peek(offset=-1)
            right = self._factor()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _factor(self) -> Expr:
        expr = self._unary()

        while self._match(TokenType.STAR, TokenType.SLASH):
            operator = self._peek(offset=-1)
            right = self._unary()
            expr = BinaryExpr(expr, operator, right)

        return expr

    def _unary(self) -> Expr:
        if self._match(TokenType.BANG, TokenType.MINUS):
            operator = self._peek(offset=-1)
            expr = self._unary()
            return UnaryExpr(operator, expr)

        return self._call()

    def _call(self) -> Expr:
        expr: Expr = self._primary()

        while True:
            if self._match(TokenType.LEFT_PAREN):
                expr = self._finish_call(expr)
            else:
                break

        return expr

    def _finish_call(self, callee: Expr) -> CallExpr:
        arguments: list[Expr] = []

        if not self._check(TokenType.RIGHT_PAREN):
            # quasi do-while loop
            while True:
                if len(arguments) > MAX_ARG_COUNT:
                    _message = f"Can't have more than {MAX_ARG_COUNT} arguments."
                    self._error(self._peek(), _message)

                expr = self._expression()
                arguments.append(expr)

                if not self._match(TokenType.COMMA):
                    break

        paren = self._consume(TokenType.RIGHT_PAREN, "Expect ')' after arguments.")

        return CallExpr(callee, paren, arguments)

    def _primary(self) -> LiteralExpr | VariableExpr | GroupingExpr:
        if self._match(TokenType.TRUE):
            return LiteralExpr(True)
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        if self._match(TokenType.NIL):
            return LiteralExpr(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            token = self._peek(offset=-1)
            return LiteralExpr(token.literal)

        if self._match(TokenType.IDENTIFIER):
            return VariableExpr(self._peek(offset=-1))

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)

        raise self._error(self._peek(), "Expect expression.")
