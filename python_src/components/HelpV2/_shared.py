from __future__ import annotations

from typing import Any


DEFAULT_COMMANDS = [
    {"name": "/help", "description": "Show DeepSeek Code help."},
    {"name": "/status", "description": "Show current model, cwd, and tool status."},
    {"name": "/write", "description": "Write a file from multiline terminal input."},
    {"name": "/append", "description": "Append text to a file."},
    {"name": "/compact", "description": "Compact local conversation context."},
    {"name": "/exit", "description": "Exit the terminal."},
]


def help_payload(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload

