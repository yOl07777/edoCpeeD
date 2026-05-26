"""DeepSeek prompt shim for performance issue investigation."""

from __future__ import annotations

from typing import Any

ALLOWED_TOOLS = ["Read", "Grep", "Glob", "Bash(git status:*)", "Bash(git diff:*)", "Bash(*test*)"]


def buildPerfIssuePrompt(args: str = "") -> str:
    focus = args.strip() or "the current performance issue"
    return f"""Investigate {focus} with DeepSeek Code.

## Constraints

- Find concrete performance bottlenecks backed by code, measurements, or reproducible symptoms.
- Do not perform broad rewrites.
- Do not introduce caching unless invalidation and memory behavior are clear.
- Avoid speculative micro-optimizations.
- Preserve public behavior and unrelated user changes.

## Expected output

- Hypothesis and evidence.
- Minimal code changes, if a fix is justified.
- Verification or benchmark command run, if available.
- Remaining risk and recommended follow-up."""


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    return [{"type": "text", "text": buildPerfIssuePrompt(args)}]


perf_issue = {
    "type": "prompt",
    "name": "perf-issue",
    "description": "Prepare a DeepSeek prompt for focused performance investigation",
    "progressMessage": "preparing performance investigation",
    "allowedTools": ALLOWED_TOOLS,
    "source": "builtin",
    "isHidden": True,
    "getPromptForCommand": getPromptForCommand,
}

default = perf_issue
