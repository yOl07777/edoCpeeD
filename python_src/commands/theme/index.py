"""Command metadata for `/theme`."""

from __future__ import annotations

from .theme import call

theme = {
    "type": "local-jsx",
    "name": "theme",
    "description": "Change the theme",
    "call": call,
}

default = theme
