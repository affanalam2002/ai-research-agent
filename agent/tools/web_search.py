from dataclasses import dataclass
from typing import Any

from ddgs import DDGS


@dataclass
class WebSearchTool:
    name: str = "web_search"
    description: str = (
        "Search the web for a query. Returns up to 5 results with title, snippet, "
        "and URL. Use this to find sources before fetching full article text."
    )
    input_schema: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.input_schema = {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "What to search for",
                }
            },
            "required": ["query"],
        }

    def run(self, query: str) -> str:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
        if not results:
            return "No results."
        lines = []
        for i, r in enumerate(results, start=1):
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            href = r.get("href", "").strip()
            lines.append(f"[{i}] {title}\n    {body}\n    {href}")
        return "\n".join(lines)
