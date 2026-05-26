from __future__ import annotations

from typing import Any

from importlib import import_module


async def KeyboardShortcutHint(*args: Any, **kwargs: Any) -> Any:
    shared = import_module("python_src.components.design-system._shared")
    keys = kwargs.get("keys") or list(args) or []
    if isinstance(keys, str):
        keys = [keys]
    return shared.ui_payload("keyboard_shortcut_hint", keys=keys, text=" + ".join(str(key) for key in keys))


__all__ = ["KeyboardShortcutHint"]
