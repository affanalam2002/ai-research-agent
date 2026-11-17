from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from anthropic import Anthropic
from rich.console import Console

from .tools import ToolRegistry, default_registry


SYSTEM_PROMPT = """You are a careful research assistant with access to tools.

When a question requires up-to-date or specific facts, use web_search first to \
find sources, then fetch_url to read the most promising pages. Cite the URLs \
you drew from in your final answer. If arithmetic matters, use python_calc \
rather than computing in your head. If the user asks you to remember \
something, use save_note.

Be concise. Stop calling tools once you have enough to answer."""


@dataclass
class Agent:
    client: Anthropic
    registry: ToolRegistry
    model: str = "claude-sonnet-5-5"
    max_turns: int = 10
    console: Console = field(default_factory=Console)
    verbose: bool = False

    def run(self, question: str) -> str:
        messages: list[dict[str, Any]] = [{"role": "user", "content": question}]

        for turn in range(self.max_turns):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                tools=self.registry.specs,
                messages=messages,
            )

            # Record the assistant message so the conversation stays coherent.
            messages.append({"role": "assistant", "content": response.content})

            if response.stop_reason == "end_turn":
                return self._extract_text(response.content)

            if response.stop_reason != "tool_use":
                # stop_sequence, max_tokens, refusal, etc. — hand back what we have.
                return self._extract_text(response.content) or f"[stopped: {response.stop_reason}]"

            tool_results: list[dict[str, Any]] = []
            for block in response.content:
                if block.type != "tool_use":
                    continue
                if self.verbose:
                    self.console.print(
                        f"[dim]→ {block.name}({self._format_args(block.input)})[/dim]"
                    )
                output, is_error = self.registry.dispatch(block.name, block.input or {})
                if self.verbose:
                    preview = output if len(output) < 400 else output[:400] + "…"
                    style = "red" if is_error else "cyan"
                    self.console.print(f"[{style}]← {preview}[/{style}]\n")
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                        "is_error": is_error,
                    }
                )

            messages.append({"role": "user", "content": tool_results})

        return "[stopped: hit max_turns without a final answer]"

    @staticmethod
    def _extract_text(content: list[Any]) -> str:
        return "".join(b.text for b in content if getattr(b, "type", None) == "text").strip()

    @staticmethod
    def _format_args(args: dict[str, Any] | None) -> str:
        if not args:
            return ""
        return ", ".join(f"{k}={v!r}" for k, v in args.items())


def run(
    question: str,
    *,
    api_key: str | None = None,
    model: str = "claude-sonnet-5-5",
    max_turns: int = 10,
    verbose: bool = False,
) -> str:
    client = Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    agent = Agent(
        client=client,
        registry=default_registry(),
        model=model,
        max_turns=max_turns,
        verbose=verbose,
    )
    return agent.run(question)
