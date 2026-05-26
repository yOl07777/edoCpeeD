from __future__ import annotations

from typing import Any


def useStdin(*args: Any, **kwargs: Any) -> dict[str, Any]:
    raw_mode = bool(kwargs.get("isRawModeEnabled", kwargs.get("rawMode", False)))
    supported = bool(kwargs.get("isRawModeSupported", True))

    def setRawMode(enabled: bool) -> dict[str, Any]:
        nonlocal raw_mode
        raw_mode = bool(enabled) and supported
        return {"provider": "deepseek", "isRawModeEnabled": raw_mode}

    return {
        "provider": "deepseek",
        "stdin": kwargs.get("stdin"),
        "isRawModeSupported": supported,
        "isRawModeEnabled": raw_mode,
        "setRawMode": setRawMode,
    }


default = useStdin
_module_migration_placeholder = useStdin
