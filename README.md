# AI Research Agent

[![CI](https://github.com/affanalam2002/ai-research-agent/actions/workflows/ci.yml/badge.svg)](https://github.com/affanalam2002/ai-research-agent/actions/workflows/ci.yml)

A terminal agent that can search the web, read articles, do math, and save notes — all orchestrated by Claude's native tool use. Ask a research question, watch it work.

Built to demonstrate how to wire Claude's tool-use loop cleanly: a typed tool registry, bounded iteration, readable traces, and handling the edge cases (parallel tool calls, max turns, malformed JSON, tool errors) that break most demos.

## Stack

Python 3.11 · Anthropic SDK · DDGS (DuckDuckGo search) · httpx · trafilatura · rich (terminal UI)

## Example run

```
$ python -m agent "What was Anthropic's last funding round size and who led it?"

→ web_search(query="Anthropic latest funding round 2025")
← 5 results
→ fetch_url(url="https://…")
← 2,134 chars of article text
→ fetch_url(url="https://…")
← 1,802 chars of article text

Anthropic closed a $4B round led by Amazon in November 2024 [source: …].
```

## Quick start

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # set ANTHROPIC_API_KEY
python -m agent "your research question"
```

Pass `--verbose` to see the full tool-call trace. Pass `--max-turns N` to bound iteration (default 10).

## How the tool loop works

```
┌─ user question ──► Claude ─┐
│                            │
│     tool_use blocks        │  Claude decides which tool(s) to call
│                            │
└─ tool_result blocks ◄──────┘  We dispatch, append results, loop until stop
```

The core loop is in [`agent/agent.py`](agent/agent.py) and fits on one screen. Every tool call is traced; a bounded turn count prevents infinite loops; a tool raising an exception returns an `is_error: true` result to the model instead of crashing the session.

## Tools

Each tool lives in `agent/tools/`. Adding a new one is a ~20-line file that implements:

```python
class Tool(Protocol):
    name: str
    description: str
    input_schema: dict        # JSON Schema
    def run(self, **kwargs) -> str: ...
```

Built-in tools:

| Tool          | What it does                                       |
| ------------- | -------------------------------------------------- |
| `web_search`  | DuckDuckGo search, returns titles + snippets + URLs |
| `fetch_url`   | Fetches a URL, extracts clean article text         |
| `python_calc` | Evaluates a math expression safely (no I/O, no builtins beyond math) |
| `save_note`   | Appends a note to `notes.md` in the working directory |

## Tests

```bash
pytest
```

Tests cover: the safe math evaluator's allowlist (no file I/O, no imports, no attribute access), the tool registry's dispatch, and the agent's handling of a malformed tool call.

## Design notes

- **Why tool use, not agent frameworks?** LangChain/LangGraph add indirection that obscures what's actually happening. The raw Anthropic tool-use API is ~40 lines of loop code and easier to reason about.
- **Why `ast.parse` for the calculator?** `eval` is a foot-gun. An AST walk with an opcode allowlist is small, auditable, and safe.
- **Why `trafilatura`?** `BeautifulSoup` dumps navigation and ads into the context. `trafilatura` gives you main-article text, which keeps the model focused.

## License

MIT
