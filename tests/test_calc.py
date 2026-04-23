import math

import pytest

from agent.tools.base import ToolError
from agent.tools.python_calc import PythonCalcTool, safe_eval


def test_basic_arithmetic():
    assert safe_eval("1 + 2") == 3
    assert safe_eval("10 - 4") == 6
    assert safe_eval("3 * 7") == 21
    assert safe_eval("9 / 2") == 4.5
    assert safe_eval("9 // 2") == 4
    assert safe_eval("9 % 4") == 1


def test_precedence_and_parens():
    assert safe_eval("(1 + 2) * 3") == 9
    assert safe_eval("1 + 2 * 3") == 7


def test_power_and_unary():
    assert safe_eval("2 ** 8") == 256
    assert safe_eval("-5 + 3") == -2
    assert safe_eval("+4") == 4


def test_rejects_name_reference():
    with pytest.raises(ToolError):
        safe_eval("os")


def test_rejects_function_call():
    with pytest.raises(ToolError):
        safe_eval("abs(-1)")


def test_rejects_attribute_access():
    with pytest.raises(ToolError):
        safe_eval("(1).__class__")


def test_rejects_import_attempt():
    with pytest.raises(ToolError):
        safe_eval("__import__('os')")


def test_rejects_string_literal():
    with pytest.raises(ToolError):
        safe_eval("'hello'")


def test_rejects_list_comprehension():
    with pytest.raises(ToolError):
        safe_eval("[x for x in range(10)]")


def test_syntax_error_becomes_tool_error():
    with pytest.raises(ToolError):
        safe_eval("1 +")


def test_pretty_print_integer():
    tool = PythonCalcTool()
    assert tool.run(expression="4 * 5") == "20"


def test_pretty_print_float():
    tool = PythonCalcTool()
    result = tool.run(expression="1 / 3")
    assert result.startswith("0.3333")
    assert math.isclose(float(result), 1 / 3, rel_tol=1e-4)
