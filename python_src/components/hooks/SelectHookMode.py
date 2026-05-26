from __future__ import annotations

from typing import Any

from python_src.components.hooks._shared import HOOK_MODES, hook_payload


async def SelectHookMode(*args: Any, **kwargs: Any) -> Any:
    selected = str(kwargs.get("mode") or kwargs.get("selected") or (args[0] if args else "view"))
    return hook_payload(
        "select_hook_mode",
        selected=selected,
        modes=[{"id": mode, "selected": mode == selected} for mode in HOOK_MODES],
        valid=selected in HOOK_MODES,
    )


__all__ = ["SelectHookMode"]
