from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SaveNoteTool:
    name: str = "save_note"
    description: str = (
        "Append a note to notes.md in the working directory. Use this to record "
        "findings the user should keep after the session ends."
    )
    path: Path = Path("notes.md")
    input_schema: dict[str, Any] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        self.input_schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Short heading"},
                "body": {"type": "string", "description": "Markdown body"},
            },
            "required": ["title", "body"],
        }

    def run(self, title: str, body: str) -> str:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n## {title}\n_{stamp}_\n\n{body}\n"
        self.path.open("a", encoding="utf-8").write(entry)
        return f"Saved note '{title}' to {self.path}"
