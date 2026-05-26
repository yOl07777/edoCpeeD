from __future__ import annotations

from typing import Any

StdinContext: dict[str, Any] = {"provider": "deepseek", "isRawModeSupported": True, "isRawModeEnabled": False}


def createStdinContext(**kwargs: Any) -> dict[str, Any]:
    context = dict(StdinContext)
    context.update(kwargs)
    return context


default = StdinContext
_module_migration_placeholder = createStdinContext
