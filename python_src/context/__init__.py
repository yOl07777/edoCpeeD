"""Context package facade for the migrated `src/context.ts` module."""

from __future__ import annotations

import importlib.util
from pathlib import Path


_module_path = Path(__file__).resolve().parent.parent / "context.py"
_spec = importlib.util.spec_from_file_location("python_src._context_facade", _module_path)
if _spec and _spec.loader:
    _module = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_module)
    for _name, _value in vars(_module).items():
        if not _name.startswith("_"):
            globals()[_name] = _value

__all__ = sorted(name for name in globals() if not name.startswith("_"))
