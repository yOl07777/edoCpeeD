from __future__ import annotations

from typing import Any

from python_src.components.sandbox._shared import sandbox_payload


async def SandboxConfigTab(*args: Any, **kwargs: Any) -> Any:
    config = kwargs.get("config") or (args[0] if args else {}) or {}
    return sandbox_payload("sandbox_config_tab", config=config, enabled=bool(config.get("enabled", True)) if isinstance(config, dict) else True)


__all__ = ["SandboxConfigTab"]
