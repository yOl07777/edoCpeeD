"""Command metadata for `/chrome`."""

from __future__ import annotations

from python_src.bootstrap.state import getIsNonInteractiveSession

from .chrome import call, getChromeStatus, setChromeDefaultEnabled


chrome = {
    "name": "chrome",
    "description": "DeepSeek browser-control settings",
    "availability": ["deepseek"],
    "isEnabled": lambda: not bool(getIsNonInteractiveSession()),
    "type": "local-jsx",
    "call": call,
}

default = chrome

__all__ = ["call", "chrome", "default", "getChromeStatus", "setChromeDefaultEnabled"]
