from dataclasses import dataclass
from typing import Any

import httpx
import trafilatura

from .base import ToolError


MAX_CHARS = 8000
TIMEOUT_SECONDS = 15


@dataclass
class FetchUrlTool:
    name: str = "fetch_url"
    description: str = (
        "Fetch a URL and return its main article text, stripped of navigation and ads. "
        f"Returns up to {MAX_CHARS} characters."
    )
    input_schema: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.input_schema = {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "The URL to fetch. Must start with http:// or https://.",
                }
            },
            "required": ["url"],
        }

    def run(self, url: str) -> str:
        if not url.startswith(("http://", "https://")):
            raise ToolError("URL must start with http:// or https://")
        try:
            response = httpx.get(
                url,
                timeout=TIMEOUT_SECONDS,
                follow_redirects=True,
                headers={"User-Agent": "ai-research-agent/1.0"},
            )
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise ToolError(f"Fetch failed: {exc}") from exc

        extracted = trafilatura.extract(response.text) or ""
        text = extracted.strip()
        if not text:
            raise ToolError("No main content could be extracted from this page.")
        if len(text) > MAX_CHARS:
            text = text[:MAX_CHARS] + "\n\n[…truncated]"
        return text
