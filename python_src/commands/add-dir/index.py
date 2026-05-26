from __future__ import annotations

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("_add_dir_command", Path(__file__).with_name("add-dir.py"))
_module = importlib.util.module_from_spec(_spec)
assert _spec and _spec.loader
_spec.loader.exec_module(_module)
call = _module.call

addDir = {
    "type": "local-jsx",
    "name": "add-dir",
    "description": "Add a new working directory",
    "argumentHint": "<path>",
    "call": call,
}

default = addDir
