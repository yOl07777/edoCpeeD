"""Command metadata for `/help`."""

from __future__ import annotations

from .help import call

help = {
    "type": "local-jsx",
    "name": "help",
    "description": "Show help and available commands",
    "call": call,
}

default = help
