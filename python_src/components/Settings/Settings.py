from __future__ import annotations

from typing import Any

from python_src.components.Settings.Config import Config
from python_src.components.Settings.Status import Status
from python_src.components.Settings.Usage import Usage
from python_src.components.Settings._shared import settings_payload


async def Settings(*args: Any, **kwargs: Any) -> Any:
    config = kwargs.get("config") or (args[0] if args else {}) or {}
    return settings_payload(
        "settings",
        config=await Config(config),
        status=await Status(config=config, diagnostics=kwargs.get("diagnostics", [])),
        usage=await Usage(kwargs.get("usage", {})),
        tabs=["config", "status", "usage"],
    )


__all__ = ["Settings"]
