from __future__ import annotations

from typing import Any

from python_src.components.hooks._shared import hook_payload, normalize_hook


async def ViewHookMode(*args: Any, **kwargs: Any) -> Any:
    hooks = kwargs.get("hooks") or (args[0] if args else []) or []
    rows = [normalize_hook(hook) for hook in hooks]
    return hook_payload(
        "view_hook_mode",
        hooks=rows,
        count=len(rows),
        empty=len(rows) == 0,
        summary=[f"{hook['event']} {hook['matcher']} -> {hook['command']}" for hook in rows],
    )


__all__ = ["ViewHookMode"]
