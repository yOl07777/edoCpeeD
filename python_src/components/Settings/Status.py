from __future__ import annotations

from typing import Any

from python_src.components.Settings._shared import settings_payload


async def buildDiagnostics(*args: Any, **kwargs: Any) -> Any:
    diagnostics = kwargs.get("diagnostics") or (args[0] if args else []) or []
    rows = [item if isinstance(item, dict) else {"name": str(item), "ok": True} for item in diagnostics]
    return {"items": rows, "ok": all(bool(item.get("ok", False)) for item in rows) if rows else True}


async def Status(*args: Any, **kwargs: Any) -> Any:
    diagnostics = await buildDiagnostics(kwargs.get("diagnostics", []))
    config = kwargs.get("config") or (args[0] if args else {}) or {}
    return settings_payload("settings_status", ok=diagnostics["ok"], diagnostics=diagnostics["items"], configured=bool(config))


__all__ = ["Status", "buildDiagnostics"]
