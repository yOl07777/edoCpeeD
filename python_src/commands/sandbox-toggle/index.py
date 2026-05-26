"""Command metadata for `/sandbox`."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_path = Path(__file__).with_name("sandbox-toggle.py")
_spec = importlib.util.spec_from_file_location("sandbox_toggle_command_impl", _path)
_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_module)
call = _module.call

sandboxToggle = {
    "type": "local",
    "name": "sandbox",
    "aliases": ["sandbox-toggle"],
    "description": "Configure local sandbox settings",
    "progressMessage": "configuring sandbox",
    "source": "builtin",
    "call": call,
}

default = sandboxToggle
