"""Hidden local Think Back player shim."""

from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any, Callable


def _load_impl():
    path = Path(__file__).with_name("thinkback-play.py")
    spec = importlib.util.spec_from_file_location("deepseek_thinkback_play_impl", path)
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
    return await _load_impl().call(onDone, context, args)


thinkback_play = {
    "type": "local",
    "name": "thinkback-play",
    "description": "Inspect local Think Back animation assets",
    "isHidden": True,
    "supportsNonInteractive": True,
    "source": "builtin",
    "call": call,
}

default = thinkback_play
