"""Implementation module for the DeepSeek upgrade command."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable


def _load_index():
    path = Path(__file__).with_name("index.py")
    spec = importlib.util.spec_from_file_location("deepseek_upgrade_index", path)
    if not spec or not spec.loader:
        raise ImportError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    return await _load_index().call(onDone, context, args)
