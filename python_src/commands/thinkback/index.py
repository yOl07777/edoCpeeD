"""DeepSeek Think Back command shim."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable


def _load_impl():
    path = Path(__file__).with_name("thinkback.py")
    spec = importlib.util.spec_from_file_location("deepseek_thinkback_impl", path)
    if not spec or not spec.loader:
        raise ImportError(f"Unable to load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def call(
    onDone: Callable[..., Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    return await _load_impl().call(onDone, context, args)


thinkback = {
    "type": "local",
    "name": "think-back",
    "aliases": ["thinkback"],
    "description": "Prepare a DeepSeek Code year-in-review prompt",
    "source": "builtin",
    "supportsNonInteractive": True,
    "call": call,
}

default = thinkback
