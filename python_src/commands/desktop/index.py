"""Command metadata for `/desktop`."""

from __future__ import annotations

from .desktop import call, getDesktopHandoffInfo, isSupportedPlatform


desktop = {
    "type": "local-jsx",
    "name": "desktop",
    "aliases": ["app"],
    "description": "Continue the current session in DeepSeek Desktop",
    "availability": ["deepseek"],
    "isEnabled": isSupportedPlatform,
    "isHidden": lambda: not isSupportedPlatform(),
    "call": call,
}

default = desktop

__all__ = ["call", "desktop", "default", "getDesktopHandoffInfo", "isSupportedPlatform"]
