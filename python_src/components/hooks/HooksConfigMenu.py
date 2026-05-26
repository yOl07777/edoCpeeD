from __future__ import annotations

from typing import Any

from python_src.components.hooks._shared import HOOK_MODES, hook_payload, normalize_hook


async def HooksConfigMenu(*args: Any, **kwargs: Any) -> Any:
    hooks = kwargs.get("hooks") or (args[0] if args else []) or []
    rows = [normalize_hook(hook) for hook in hooks]
    selected = str(kwargs.get("mode") or "view")
    return hook_payload(
        "hooks_config_menu",
        hooks=rows,
        count=len(rows),
        mode=selected,
        modes=[{"id": mode, "selected": mode == selected} for mode in HOOK_MODES],
        actions=["add", "edit", "remove", "test"],
    )


__all__ = ["HooksConfigMenu"]
