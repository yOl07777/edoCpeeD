"""Generate a keybindings.json template for the Python runtime."""

from __future__ import annotations

import json
from typing import Any


DEFAULT_TEMPLATE_BINDINGS: list[dict[str, Any]] = [
    {
        "context": "Global",
        "bindings": {
            "ctrl+o": "app:toggleTranscript",
            "ctrl+t": "app:toggleTodos",
        },
    },
    {
        "context": "Chat",
        "bindings": {
            "escape": "chat:cancel",
            "enter": "chat:submit",
            "ctrl+r": "history:search",
        },
    },
]


def generateKeybindingsTemplate() -> str:
    config = {
        "$schema": "https://www.schemastore.org/claude-code-keybindings.json",
        "$docs": "https://code.claude.com/docs/en/keybindings",
        "bindings": DEFAULT_TEMPLATE_BINDINGS,
    }
    return json.dumps(config, ensure_ascii=False, indent=2) + "\n"
