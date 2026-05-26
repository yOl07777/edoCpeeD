from __future__ import annotations

from typing import Any

from python_src.components.sandbox._shared import sandbox_payload


async def SandboxOverridesTab(*args: Any, **kwargs: Any) -> Any:
    overrides = kwargs.get("overrides") or (args[0] if args else []) or []
    if isinstance(overrides, dict):
        overrides = [{"name": key, "value": value} for key, value in overrides.items()]
    return sandbox_payload("sandbox_overrides_tab", overrides=overrides, count=len(overrides))


__all__ = ["SandboxOverridesTab"]
