"""Command metadata for `/install-slack-app`."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


_impl_path = Path(__file__).with_name("install-slack-app.py")
_spec = importlib.util.spec_from_file_location("python_src.commands.install_slack_app_impl", _impl_path)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError(f"Unable to load {_impl_path}")
_impl = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _impl
_spec.loader.exec_module(_impl)

call = _impl.call
SLACK_APP_URL = _impl.SLACK_APP_URL

installSlackApp: dict[str, Any] = {
    "type": "local",
    "name": "install-slack-app",
    "description": "Show DeepSeek Slack integration setup guidance",
    "availability": ["deepseek"],
    "supportsNonInteractive": False,
    "source": "builtin",
    "call": call,
}

default = installSlackApp

__all__ = ["SLACK_APP_URL", "call", "default", "installSlackApp"]
