"""Command metadata for `/export`."""

from __future__ import annotations

from .export import call

exportCommand = {
    "type": "local-jsx",
    "name": "export",
    "description": "Export the current conversation to a file or clipboard",
    "argumentHint": "[filename]",
    "call": call,
}

default = exportCommand
