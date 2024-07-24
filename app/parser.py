from collections.abc import Sequence
from app.errors import ParserError
from app.expression import BinaryExpr, Expr, GroupingExpr, LiteralExpr, UnaryExpr
from app.logger import Logger
from app.schema import Token, TokenType


class Parser:
    _logger: Logger
    _tokens: list[Token]
    _current: int

    def __init__(self, _logger: Logger, _tokens: Sequence[Token]) -> None:
        self._logger = _logger

        self._tokens = list(_tokens)
        self._current = 0

    def parse(self) -> Expr | None:
        try:
            return self._expression()
        except ParserError:
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

    def _error(self, token: Token, message: str) -> ParserError:
        where = "end" if token.type_ == TokenType.EOF else f"'{token.lexeme}'"
        self._logger.report(token.line, f" at {where}", message)

        return ParserError()

    def _expression(self) -> Expr:
        return self._equality()

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

        return self._primary()

    def _primary(self) -> Expr:
        if self._match(TokenType.TRUE):
            return LiteralExpr(True)
        if self._match(TokenType.FALSE):
            return LiteralExpr(False)
        if self._match(TokenType.NIL):
            return LiteralExpr(None)

        if self._match(TokenType.NUMBER, TokenType.STRING):
            token = self._peek(offset=-1)
            return LiteralExpr(token.literal)

        if self._match(TokenType.LEFT_PAREN):
            expr = self._expression()
            self._consume(TokenType.RIGHT_PAREN, "Expect ')' after expression.")
            return GroupingExpr(expr)

        raise self._error(self._peek(), "Expect expression.")
