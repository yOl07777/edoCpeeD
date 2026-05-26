"""Command metadata for `/tag`."""

from __future__ import annotations

from .tag import call, getCurrentSessionTag, saveTag

tag = {
    "type": "local",
    "name": "tag",
    "description": "Toggle a searchable tag on the current session",
    "progressMessage": "tagging session",
    "source": "builtin",
    "call": call,
}

default = tag
