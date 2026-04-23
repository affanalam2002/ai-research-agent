from typing import Any

from .base import Tool, ToolError
from .fetch_url import FetchUrlTool
from .python_calc import PythonCalcTool
from .save_note import SaveNoteTool
from .web_search import WebSearchTool


class ToolRegistry:
    """Holds tools and exposes them in Anthropic's tool schema shape."""

    def __init__(self, tools: list[Tool]) -> None:
        self._tools: dict[str, Tool] = {t.name: t for t in tools}

    @property
    def specs(self) -> list[dict[str, Any]]:
        return [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.input_schema,
            }
            for t in self._tools.values()
        ]

    def dispatch(self, name: str, arguments: dict[str, Any]) -> tuple[str, bool]:
        """Run a tool by name. Returns (output, is_error)."""
        tool = self._tools.get(name)
        if tool is None:
            return f"Unknown tool '{name}'", True
        try:
            return tool.run(**arguments), False
        except ToolError as exc:
            return str(exc), True
        except TypeError as exc:
            return f"Bad arguments for {name}: {exc}", True
        except Exception as exc:  # last-resort safety net
            return f"{type(exc).__name__}: {exc}", True


def default_registry() -> ToolRegistry:
    return ToolRegistry(
        [WebSearchTool(), FetchUrlTool(), PythonCalcTool(), SaveNoteTool()]
    )
