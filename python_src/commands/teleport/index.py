"""Hidden teleport prompt shim for DeepSeek Code."""

from __future__ import annotations

from typing import Any


def buildTeleportPrompt(args: str = "") -> str:
    target = args.strip() or "a fresh DeepSeek Code session"
    return f"""Prepare a handoff package for {target}.

Include:
- Current objective.
- Important files and commands already inspected.
- Decisions made and why.
- Remaining tasks in priority order.
- Known blockers, missing dependencies, and verification status.

Do not edit files. Return concise markdown that another DeepSeek Code session can continue from."""


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    return [{"type": "text", "text": buildTeleportPrompt(args)}]


teleport = {
    "type": "prompt",
    "name": "teleport",
    "description": "Prepare a DeepSeek session handoff prompt",
    "progressMessage": "preparing handoff",
    "allowedTools": [],
    "source": "builtin",
    "isHidden": True,
    "getPromptForCommand": getPromptForCommand,
}

default = teleport
