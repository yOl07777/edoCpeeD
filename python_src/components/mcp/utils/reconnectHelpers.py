from __future__ import annotations

from typing import Any


async def handleReconnectError(*args: Any, **kwargs: Any) -> Any:
    error = kwargs.get("error") or (args[0] if args else None)
    return {
        "provider": "deepseek",
        "ok": False,
        "error": str(error or "Reconnect failed"),
        "retryable": bool(kwargs.get("retryable", True)),
    }


async def handleReconnectResult(*args: Any, **kwargs: Any) -> Any:
    result = kwargs.get("result") if "result" in kwargs else (args[0] if args else {})
    ok = bool(result.get("ok", True)) if isinstance(result, dict) else bool(result)
    return {
        "provider": "deepseek",
        "ok": ok,
        "message": "Reconnect succeeded" if ok else "Reconnect failed",
        "result": result,
    }


__all__ = ["handleReconnectError", "handleReconnectResult"]
