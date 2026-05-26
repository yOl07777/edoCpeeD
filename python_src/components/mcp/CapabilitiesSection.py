from __future__ import annotations

from typing import Any

from python_src.components.mcp._shared import mcp_payload


async def CapabilitiesSection(*args: Any, **kwargs: Any) -> Any:
    capabilities = kwargs.get("capabilities") or (args[0] if args else {}) or {}
    if isinstance(capabilities, list):
        rows = [{"name": str(item), "enabled": True} for item in capabilities]
    else:
        rows = [{"name": str(key), "enabled": bool(value)} for key, value in dict(capabilities).items()]
    return mcp_payload("mcp_capabilities_section", capabilities=rows, count=len(rows))


__all__ = ["CapabilitiesSection"]
