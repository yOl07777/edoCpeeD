"""DeepSeek prompt shim for the hidden autofix-pr command."""

from __future__ import annotations

from typing import Any

ALLOWED_TOOLS = [
    "Bash(git status:*)",
    "Bash(git diff:*)",
    "Bash(git log:*)",
    "Bash(gh pr view:*)",
    "Bash(gh pr checks:*)",
    "Bash(gh run view:*)",
    "Read",
    "Grep",
    "Glob",
    "Edit",
]


def buildAutofixPrPrompt(args: str = "") -> str:
    extra = args.strip()
    prompt = """## Context

- Current branch: !`git branch --show-current`
- Current git status: !`git status --short`
- Current diff: !`git diff HEAD`
- Current PR, if any: !`gh pr view --json number,title,url,headRefName,baseRefName,mergeStateStatus,statusCheckRollup`
- Current PR checks, if any: !`gh pr checks`

## DeepSeek Code autofix task

Investigate the current pull request and fix high-confidence local issues that explain failing checks or review feedback.

Rules:
- Do not commit, push, merge, close, or create a PR unless the user explicitly asks.
- Do not rewrite history or use destructive git commands.
- Prefer the smallest code change that resolves the observed failure.
- If a failure cannot be reproduced locally, explain what evidence is missing and what command should be run next.
- Preserve unrelated user changes.
- After edits, run the narrowest relevant verification command if it is discoverable from the repo.

Output:
- Briefly summarize the failing signal you used.
- List files changed.
- Report verification commands and results.
- Call out any unresolved risk."""
    if extra:
        prompt += f"\n\n## Additional user instructions\n\n{extra}"
    return prompt


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    return [{"type": "text", "text": buildAutofixPrPrompt(args)}]


autofix_pr = {
    "type": "prompt",
    "name": "autofix-pr",
    "description": "Draft a safe DeepSeek prompt to investigate and fix the current PR",
    "progressMessage": "preparing PR autofix prompt",
    "allowedTools": ALLOWED_TOOLS,
    "source": "builtin",
    "isHidden": True,
    "getPromptForCommand": getPromptForCommand,
}

default = autofix_pr
