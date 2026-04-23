import argparse
import os
import sys

from dotenv import load_dotenv
from rich.console import Console

from .agent import run


def main() -> int:
    load_dotenv()

    parser = argparse.ArgumentParser(
        prog="agent",
        description="A Claude-powered research agent with web, URL, calc, and note tools.",
    )
    parser.add_argument("question", nargs="+", help="The research question")
    parser.add_argument(
        "--model",
        default=os.environ.get("CLAUDE_MODEL", "claude-sonnet-4-6"),
        help="Claude model to use",
    )
    parser.add_argument(
        "--max-turns", type=int, default=10, help="Max tool-use iterations (default 10)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print every tool call and result"
    )
    args = parser.parse_args()

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("error: ANTHROPIC_API_KEY is not set. See .env.example.", file=sys.stderr)
        return 2

    question = " ".join(args.question)
    console = Console()
    answer = run(
        question,
        model=args.model,
        max_turns=args.max_turns,
        verbose=args.verbose,
    )
    console.rule("[bold]answer")
    console.print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
