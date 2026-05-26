"""Command metadata for `/web-setup`."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Any


_impl_path = Path(__file__).with_name("remote-setup.py")
_spec = importlib.util.spec_from_file_location("python_src.commands.remote_setup_impl", _impl_path)
if _spec is None or _spec.loader is None:  # pragma: no cover
    raise ImportError(f"Unable to load {_impl_path}")
_impl = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _impl
_spec.loader.exec_module(_impl)

call = _impl.call
checkLoginState = _impl.checkLoginState
errorMessage = _impl.errorMessage


def _enabled() -> bool:
    return True


web: dict[str, Any] = {
    "type": "local-jsx",
    "name": "web-setup",
    "aliases": ["remote-setup"],
    "description": "Set up DeepSeek Code web handoff and GitHub prerequisites",
    "availability": ["deepseek"],
    "isEnabled": _enabled,
    "isHidden": lambda: False,
    "source": "builtin",
    "call": call,
}

default = web

__all__ = ["call", "checkLoginState", "default", "errorMessage", "web"]
