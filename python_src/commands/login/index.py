"""Login command metadata."""

from __future__ import annotations

import importlib
import os
from typing import Any


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


async def _description() -> str:
    from python_src.utils.auth import hasAnthropicApiKeyAuth

    return "Switch DeepSeek accounts" if await hasAnthropicApiKeyAuth() else "Sign in with your DeepSeek API key"


default = {
    "type": "local-jsx",
    "name": "login",
    "description": _description,
    "isEnabled": lambda: not _truthy(os.getenv("DISABLE_LOGIN_COMMAND")),
    "load": lambda: importlib.import_module("python_src.commands.login.login"),
}
