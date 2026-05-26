"""Command metadata for `/release-notes`."""

from __future__ import annotations

import importlib.util
from pathlib import Path

_module_path = Path(__file__).resolve().with_name("release-notes.py")
_spec = importlib.util.spec_from_file_location("python_src.commands.release_notes.release_notes", _module_path)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Could not load {_module_path}")
_module = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_module)
call = _module.call

releaseNotes = {
    "description": "View release notes",
    "name": "release-notes",
    "type": "local",
    "supportsNonInteractive": True,
    "call": call,
}

default = releaseNotes
