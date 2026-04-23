from typing import Any, Protocol, runtime_checkable


class ToolError(Exception):
    """Raised by a tool when invocation fails in a way the model should see."""


@runtime_checkable
class Tool(Protocol):
    name: str
    description: str
    input_schema: dict[str, Any]

    def run(self, **kwargs: Any) -> str:
        ...
