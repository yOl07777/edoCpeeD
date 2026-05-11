from __future__ import annotations

from typing import Any

from python_src.hooks.toolPermission.handlers.interactiveHandler import handleInteractivePermission


async def handleCoordinatorPermission(context: dict[str, Any], rules: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    return await handleInteractivePermission(context, rules)
