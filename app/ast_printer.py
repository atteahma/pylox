from app.expression import (
    BinaryExpr,
    Expr,
    GroupingExpr,
    LiteralExpr,
    TernaryExpr,
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
        if expr.value is True:
            return "true"
        if expr.value is False:
            return "false"

        return str(expr.value)

    def visitUnaryExpr(self, expr: UnaryExpr) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.expr)

    def visitTernaryExpr(self, expr: TernaryExpr) -> str:
        return self._parenthesize("?", expr.condition, expr.true_expr, expr.false_expr)

    def print(self, expr: Expr) -> str:
        value = expr.accept(self)
        print(value)
        return value
