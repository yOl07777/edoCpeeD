from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option


async def BypassPermissionsModeDialog(*args: Any, **kwargs: Any) -> Any:
    warnings = normalize_items(option(args, kwargs, "warnings", ["File and shell tools may run with fewer prompts", "Do not enable for untrusted workspaces"]))
    return component_payload("bypass_permissions_mode_dialog", enabled=bool(option(args, kwargs, "enabled", False)), warnings=warnings)


__all__ = ["BypassPermissionsModeDialog"]
