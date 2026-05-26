"""Implementation module for the Think Back player shim."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable


def _load_thinkback():
    path = Path(__file__).parents[1] / "thinkback" / "thinkback.py"
    spec = importlib.util.spec_from_file_location("deepseek_thinkback_impl_for_play", path)
    if not spec or not spec.loader:
        raise ImportError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, str]:
    result = await _load_thinkback().playAnimation(args.strip() or None)
    value = str(result["message"])
    if onDone:
        onDone(value)
    return {"type": "text", "value": value, "path": str(result.get("path", ""))}
