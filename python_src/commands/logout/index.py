"""Logout command metadata."""

from __future__ import annotations

import importlib
import os


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


default = {
    "type": "local-jsx",
    "name": "logout",
    "description": "Sign out from your DeepSeek account",
    "isEnabled": lambda: not _truthy(os.getenv("DISABLE_LOGOUT_COMMAND")),
    "load": lambda: importlib.import_module("python_src.commands.logout.logout"),
}
