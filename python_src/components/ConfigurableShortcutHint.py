from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def ConfigurableShortcutHint(*args: Any, **kwargs: Any) -> Any:
    shortcut = str(option(args, kwargs, "shortcut", scalar_arg(args, "")))
    action = str(option(args, kwargs, "action", option(args, kwargs, "label", "")))
    return component_payload("configurable_shortcut_hint", shortcut=shortcut, action=action, text=f"{shortcut} {action}".strip())


__all__ = ["ConfigurableShortcutHint"]
