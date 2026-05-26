"""Prompt command for configuring the DeepSeek Code status line."""

from __future__ import annotations

from typing import Any

AGENT_TOOL_NAME = "Agent"
ALLOWED_TOOLS = [AGENT_TOOL_NAME, "Read(~/**)", "Edit(~/.deepseek/settings.json)", "Edit(~/.claude/settings.json)"]


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    prompt = (args or "").strip() or "Configure my DeepSeek Code statusLine from my shell PS1 configuration"
    return [
        {
            "type": "text",
            "text": (
                f'Create an {AGENT_TOOL_NAME} with subagent_type "statusline-setup" '
                f'and the prompt "{prompt}". Prefer writing statusLine settings to '
                "~/.deepseek/settings.json, while preserving ~/.claude/settings.json compatibility if it already exists."
            ),
        }
    ]


statusline = {
    "type": "prompt",
    "name": "statusline",
    "description": "Set up DeepSeek Code's status line UI",
    "contentLength": 0,
    "aliases": [],
    "progressMessage": "setting up statusLine",
    "allowedTools": ALLOWED_TOOLS,
    "source": "builtin",
    "disableNonInteractive": True,
    "getPromptForCommand": getPromptForCommand,
}

default = statusline
