"""Safe arithmetic evaluator.

Why not ``eval``? It will happily execute ``__import__('os').system(...)``.
Instead we parse the expression to an AST and walk it with a strict allowlist:
no names, no calls, no attribute access, no comprehensions. Only numbers and
the arithmetic operators below.
"""

from __future__ import annotations

import ast
import math
import operator
from dataclasses import dataclass
from typing import Any

from .base import ToolError


_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
    ast.Pow: operator.pow,
}

_UNARYOPS = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}


def safe_eval(expression: str) -> float:
    try:
        tree = ast.parse(expression, mode="eval")
    except SyntaxError as exc:
        raise ToolError(f"Invalid syntax: {exc.msg}") from exc

    def _eval(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return _eval(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.BinOp) and type(node.op) in _BINOPS:
            return _BINOPS[type(node.op)](_eval(node.left), _eval(node.right))
        if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARYOPS:
            return _UNARYOPS[type(node.op)](_eval(node.operand))
        raise ToolError(f"Disallowed expression: {ast.dump(node)}")

    return _eval(tree)


@dataclass
class PythonCalcTool:
    name: str = "python_calc"
    description: str = (
        "Evaluate a numeric expression. Supports + - * / // % ** and parentheses. "
        "Does NOT support variables, functions, or anything other than arithmetic."
    )
    input_schema: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.input_schema = {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "The expression, e.g. '(1200 - 340) * 0.08'",
                }
            },
            "required": ["expression"],
        }

    def run(self, expression: str) -> str:
        result = safe_eval(expression)
        # Pretty-print integers as integers
        if math.isfinite(result) and result == int(result):
            return str(int(result))
        return f"{result:.6g}"
