"""Hidden local trace prompt shim."""

from __future__ import annotations

from typing import Any


def buildTracePrompt(args: str = "") -> str:
    focus = args.strip() or "the current DeepSeek Code execution path"
    return f"""Trace {focus}.

Produce a concise diagnostic note with:
- Entry point and relevant command/tool modules.
- State stores or config files touched.
- External commands or network calls that would be involved.
- Places where Claude-specific behavior has been replaced by DeepSeek/OpenAI-compatible behavior.
- Safe next verification command.

Do not edit files and do not run destructive commands."""


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    return [{"type": "text", "text": buildTracePrompt(args)}]


ant_trace = {
    "type": "prompt",
    "name": "ant-trace",
    "description": "Prepare a hidden DeepSeek diagnostic trace prompt",
    "progressMessage": "preparing trace",
    "allowedTools": ["Read", "Grep", "Glob", "Bash(git status:*)"],
    "source": "builtin",
    "isHidden": True,
    "getPromptForCommand": getPromptForCommand,
}

default = ant_trace
