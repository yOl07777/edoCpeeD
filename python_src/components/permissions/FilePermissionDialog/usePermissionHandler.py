from __future__ import annotations

from typing import Any

from python_src.hooks.toolPermission.handlers.interactiveHandler import handleInteractivePermission


async def allow_once(context: dict[str, Any] | None = None, **_kwargs: Any) -> dict[str, Any]:
    return {"behavior": "allow", "scope": "once", "context": context or {}}


async def deny(context: dict[str, Any] | None = None, **_kwargs: Any) -> dict[str, Any]:
    return {"behavior": "deny", "scope": "once", "context": context or {}}


async def ask(context: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    return await handleInteractivePermission(context or {}, rules=kwargs.get("rules"))


PERMISSION_HANDLERS: dict[str, Any] = {
    "allow_once": allow_once,
    "allow": allow_once,
    "deny": deny,
    "ask": ask,
}


__all__ = ["PERMISSION_HANDLERS", "allow_once", "ask", "deny"]
