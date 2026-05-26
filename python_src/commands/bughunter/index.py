"""DeepSeek prompt shim for the hidden bughunter command."""

from __future__ import annotations

from typing import Any

ALLOWED_TOOLS = [
    "Bash(git status:*)",
    "Bash(git diff:*)",
    "Bash(git log:*)",
    "Bash(*test*)",
    "Read",
    "Grep",
    "Glob",
    "Edit",
]


def buildBughunterPrompt(args: str = "") -> str:
    extra = args.strip()
    prompt = """You are DeepSeek Code running a focused bug hunt in this repository.

## Context to inspect

- Git status: !`git status --short`
- Current diff: !`git diff HEAD`
- Recent commits: !`git log --oneline -8`

## Task

Find and fix high-confidence correctness bugs in the current working tree or in the area described by the user.

Rules:
- Prioritize real correctness, data loss, security, crash, and test-failure risks.
- Do not report style issues, speculative edge cases, or broad refactors.
- Keep changes minimal and compatible with the existing code style.
- Do not commit or push.
- Preserve unrelated user edits.
- Verify with targeted tests or static checks when practical.

Final response should include findings, changed files, verification, and residual risk."""
    if extra:
        prompt += f"\n\n## User focus\n\n{extra}"
    return prompt


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    return [{"type": "text", "text": buildBughunterPrompt(args)}]


bughunter = {
    "type": "prompt",
    "name": "bughunter",
    "description": "Prepare a focused DeepSeek bug-hunting prompt",
    "progressMessage": "preparing bug hunt",
    "allowedTools": ALLOWED_TOOLS,
    "source": "builtin",
    "isHidden": True,
    "getPromptForCommand": getPromptForCommand,
}

default = bughunter
