from app.expression import (
    BinaryExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    UnaryExpr,
    Visitor,
)


class AstPrinter(Visitor[str]):
    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        parts = []

        parts.append("(")
        parts.append(name)

        for expr in exprs:
            parts.append(" ")
            parts.append(expr.accept(self))

        parts.append(")")

        return "".join(parts)

    def visitBinaryExpr(self, expr: BinaryExpr) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitGroupingExpr(self, expr: GroupingExpr) -> str:
        return self._parenthesize("group", expr.expr)

    def visitLiteralExpr(self, expr: LiteralExpr) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visitUnaryExpr(self, expr: UnaryExpr) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.expr)

    def print(self, expr: Expr) -> str:
        value = expr.accept(self)
        print(value)
        return value
