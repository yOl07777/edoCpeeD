"""Command metadata for `/extra-usage`."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path
from types import ModuleType

from python_src.bootstrap.state import getIsNonInteractiveSession


def _truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def isExtraUsageAllowed() -> bool:
    return not _truthy(os.getenv("DISABLE_EXTRA_USAGE_COMMAND"))


def _load(filename: str, module_name: str) -> ModuleType:
    path = Path(__file__).with_name(filename)
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def _interactive_call(*args, **kwargs):
    module = _load("extra-usage.py", "python_src.commands.extra_usage_interactive")
    return await module.call(*args, **kwargs)


async def _noninteractive_call(*args, **kwargs):
    module = _load("extra-usage-noninteractive.py", "python_src.commands.extra_usage_noninteractive")
    return await module.call(*args, **kwargs)


extraUsage = {
    "type": "local-jsx",
    "name": "extra-usage",
    "description": "Configure DeepSeek extra usage to keep working when limits are hit",
    "isEnabled": lambda: isExtraUsageAllowed() and not bool(getIsNonInteractiveSession()),
    "call": _interactive_call,
}

extraUsageNonInteractive = {
    "type": "local",
    "name": "extra-usage",
    "supportsNonInteractive": True,
    "description": "Configure DeepSeek extra usage to keep working when limits are hit",
    "isEnabled": lambda: isExtraUsageAllowed() and bool(getIsNonInteractiveSession()),
    "isHidden": lambda: not bool(getIsNonInteractiveSession()),
    "call": _noninteractive_call,
}

default = extraUsage

__all__ = ["default", "extraUsage", "extraUsageNonInteractive", "isExtraUsageAllowed"]
