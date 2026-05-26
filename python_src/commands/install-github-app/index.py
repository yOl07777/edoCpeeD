"""Command metadata for `/install-github-app`."""

from __future__ import annotations

import os
import importlib
from typing import Any


_impl = importlib.import_module("python_src.commands.install-github-app.install-github-app")
call = _impl.call


def _is_enabled() -> bool:
    return os.environ.get("DISABLE_INSTALL_GITHUB_APP_COMMAND", "").lower() not in {"1", "true", "yes", "on"}


installGitHubApp: dict[str, Any] = {
    "type": "local-jsx",
    "name": "install-github-app",
    "description": "Generate DeepSeek GitHub Actions setup guidance for a repository",
    "availability": ["deepseek", "console"],
    "isEnabled": _is_enabled,
    "source": "builtin",
    "call": call,
}

default = installGitHubApp

__all__ = ["call", "default", "installGitHubApp"]
