from dataclasses import dataclass
from typing import Any

from agent.tools.base import ToolError
from agent.tools.registry import ToolRegistry


@dataclass
class EchoTool:
    name: str = "echo"
    description: str = "Echo back the input text."
    input_schema: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.input_schema = {
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        }

    def run(self, text: str) -> str:
        return text


@dataclass
class BrokenTool:
    name: str = "broken"
    description: str = "Always raises."
    input_schema: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.input_schema = {"type": "object", "properties": {}}

    def run(self) -> str:
        raise ToolError("nope")


def test_specs_shape():
    reg = ToolRegistry([EchoTool()])
    specs = reg.specs
    assert specs == [
        {
            "name": "echo",
            "description": "Echo back the input text.",
            "input_schema": {
                "type": "object",
                "properties": {"text": {"type": "string"}},
                "required": ["text"],
            },
        }
    ]


def test_dispatch_success():
    reg = ToolRegistry([EchoTool()])
    output, is_error = reg.dispatch("echo", {"text": "hi"})
    assert output == "hi"
    assert is_error is False


def test_dispatch_unknown_tool():
    reg = ToolRegistry([EchoTool()])
    output, is_error = reg.dispatch("missing", {})
    assert is_error is True
    assert "missing" in output


def test_dispatch_bad_arguments():
    reg = ToolRegistry([EchoTool()])
    output, is_error = reg.dispatch("echo", {"wrong_key": "hi"})
    assert is_error is True
    assert "echo" in output


def test_dispatch_tool_error_is_captured():
    reg = ToolRegistry([BrokenTool()])
    output, is_error = reg.dispatch("broken", {})
    assert is_error is True
    assert output == "nope"
