"""Command metadata for `/clear`."""

from __future__ import annotations

from .clear import call

clear_command = {
    "type": "local",
    "name": "clear",
    "description": "Clear conversation history and free up context",
    "aliases": ["reset", "new"],
    "isEnabled": lambda: True,
    "isHidden": lambda: False,
    "supportsNonInteractive": False,
    "call": call,
}

default = clear_command
