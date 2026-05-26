"""Command metadata for `/vim`."""

from __future__ import annotations

from .vim import call, getEditorMode, setEditorMode


vim = {
    "type": "local",
    "name": "vim",
    "description": "Toggle vim keybindings",
    "supportsNonInteractive": True,
    "call": call,
}

default = vim

__all__ = ["call", "default", "getEditorMode", "setEditorMode", "vim"]
