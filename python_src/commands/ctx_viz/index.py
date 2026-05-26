"""DeepSeek prompt shim for context visualization."""

from __future__ import annotations

from typing import Any

ALLOWED_TOOLS = ["Read", "Grep", "Glob", "Bash(git status:*)", "Bash(git diff:*)"]


def buildContextVizPrompt(args: str = "") -> str:
    focus = args.strip() or "the current repository and active change set"
    return f"""Create a concise context visualization for {focus}.

Use DeepSeek Code to inspect the relevant files and produce a markdown answer with:

- A small Mermaid diagram showing the main modules, data flow, or command flow.
- A short explanation of the important relationships.
- File references for the evidence used.
- Any uncertainty that should be checked before implementation.

Do not edit files. Do not run write, commit, push, install, or network commands."""


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    return [{"type": "text", "text": buildContextVizPrompt(args)}]


ctx_viz = {
    "type": "prompt",
    "name": "ctx-viz",
    "aliases": ["ctx_viz"],
    "description": "Visualize repository context with a DeepSeek-compatible prompt",
    "progressMessage": "preparing context visualization",
    "allowedTools": ALLOWED_TOOLS,
    "source": "builtin",
    "isHidden": True,
    "getPromptForCommand": getPromptForCommand,
}

default = ctx_viz
