from __future__ import annotations

from typing import Any


async def usePromptInputPlaceholder(*args: Any, **kwargs: Any) -> Any:
    mode = str(kwargs.get("mode") or (args[0] if args else "prompt"))
    placeholders = {
        "prompt": "Ask DeepSeek Code...",
        "shell": "Run a shell command...",
        "command": "Type a slash command...",
        "file": "Attach a file path...",
        "memory": "Add memory...",
        "help": "Search help...",
    }
    return placeholders.get(mode, placeholders["prompt"])


__all__ = ["usePromptInputPlaceholder"]
