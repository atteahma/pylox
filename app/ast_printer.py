import sys
from app import util
from app import expression as Expr


class AstPrinter(Expr.Visitor[str]):
    def _parenthesize(self, name: str, *exprs: Expr.Expr) -> str:
        parts = []

        parts.append("(")
        parts.append(name)

        for expr in exprs:
            parts.append(" ")
            parts.append(expr.accept(self))

        parts.append(")")

        return "".join(parts)

    def visit_binary_expr(self, expr: Expr.Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visit_grouping_expr(self, expr: Expr.Grouping) -> str:
        return self._parenthesize("group", expr.expr)

    def visit_literal_expr(self, expr: Expr.Literal) -> str:
        return util.stringify(expr.value, double_to_int=False)

    def visit_unary_expr(self, expr: Expr.Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.expr)

    def visit_ternary_expr(self, expr: Expr.Ternary) -> str:
        return self._parenthesize("?", expr.condition, expr.true_expr, expr.false_expr)

    def visit_variable_expr(self, expr: Expr.Variable) -> str:
        return expr.name.lexeme

    def visit_assign_expr(self, expr: Expr.Assign) -> str:
        return self._parenthesize(expr.name.lexeme, expr.value_expr)

    def visit_logical_expr(self, expr: Expr.Logical) -> str:
        raise NotImplementedError("AstPrinter.visit_logical_expr not implemented")

    def visit_call_expr(self, expr: Expr.Call) -> str:
        raise NotImplementedError("AstPrinter.visit_call_expr not implemented")

    def visit_get_expr(self, expr: Expr.Get) -> str:
        raise NotImplementedError("AstPrinter.visit_get_expr not implemented")

    def visit_set_expr(self, expr: Expr.Set) -> str:
        raise NotImplementedError("AstPrinter.visit_set_expr not implemented")

    def visit_this_expr(self, expr: Expr.This) -> str:
        raise NotImplementedError("AstPrinter.visit_this_expr not implemented")

    def visit_super_expr(self, expr: Expr.Super) -> str:
        raise NotImplementedError("AstPrinter.visit_super_expr not implemented")

    def print(self, expr: Expr.Expr) -> str:
        value = expr.accept(self)
        print(value, file=sys.stdout)
        return value
