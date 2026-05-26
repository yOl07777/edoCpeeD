"""Command metadata for `/files`."""

from __future__ import annotations

import os

from .files import call

files = {
    "type": "local",
    "name": "files",
    "description": "List all files currently in context",
    "isEnabled": lambda: os.getenv("USER_TYPE") == "ant" or os.getenv("DEEPSEEK_SHOW_FILES_COMMAND") == "1",
    "supportsNonInteractive": True,
    "call": call,
}

default = files
