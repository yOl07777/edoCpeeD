"""Plan command metadata."""

from __future__ import annotations

import importlib

default = {
    "type": "local-jsx",
    "name": "plan",
    "description": "Enable plan mode or view the current session plan",
    "argumentHint": "[open|<description>]",
    "load": lambda: importlib.import_module("python_src.commands.plan.plan"),
}
