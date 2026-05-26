"""Command metadata for `/rename`."""

from __future__ import annotations

from .generateSessionName import generateSessionName
from .rename import call, getSessionName, saveSessionName


rename = {
    "type": "local-jsx",
    "name": "rename",
    "description": "Rename the current session",
    "argumentHint": "[name]",
    "supportsNonInteractive": True,
    "call": call,
}

default = rename

__all__ = ["call", "default", "generateSessionName", "getSessionName", "rename", "saveSessionName"]
