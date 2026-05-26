"""Import-friendly wrapper for the hyphenated extra-usage core module."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType


def _load() -> ModuleType:
    path = Path(__file__).with_name("extra-usage-core.py")
    spec = importlib.util.spec_from_file_location("python_src.commands.extra_usage_core_impl", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_module = _load()
runExtraUsage = _module.runExtraUsage

__all__ = ["runExtraUsage"]
