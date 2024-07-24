from app import util
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


class AstPrinter(ExprVisitor[str]):
    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        parts = []

        parts.append("(")
        parts.append(name)

        for expr in exprs:
            parts.append(" ")
            parts.append(expr.accept(self))

        parts.append(")")

        return "".join(parts)

    def visit_binary_expr(self, expr: BinaryExpr) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: GroupingExpr) -> str:
        return self._parenthesize("group", expr.expr)

    def visit_literal_expr(self, expr: LiteralExpr) -> str:
        return util.stringify(expr.value, double_to_int=False)

    def visit_unary_expr(self, expr: UnaryExpr) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.expr)

    def visit_ternary_expr(self, expr: TernaryExpr) -> str:
        return self._parenthesize("?", expr.condition, expr.true_expr, expr.false_expr)

    def visit_variable_expr(self, expr: VariableExpr) -> str:
        return expr.name.lexeme

    def visit_assign_expr(self, expr: AssignExpr) -> str:
        return self._parenthesize(expr.name.lexeme, expr.value_expr)

    def visit_logical_expr(self, expr: LogicalExpr) -> str:
        raise NotImplementedError("AstPrinter.visit_logical_expr not implemented")

    def visit_call_expr(self, expr: CallExpr) -> str:
        raise NotImplementedError("AstPrinter.visit_call_expr not implemented")

    def print(self, expr: Expr) -> str:
        value = expr.accept(self)
        print(value)
        return value
