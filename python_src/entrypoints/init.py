from __future__ import annotations

import os
from typing import Any


async def initializeTelemetryAfterTrust(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    enabled = not (os.getenv("DEEPSEEK_DISABLE_TELEMETRY") == "1" or kwargs.get("disabled"))
    return {"provider": "deepseek", "telemetryEnabled": enabled, "trusted": bool(kwargs.get("trusted", True))}


async def call(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    return {"type": "init", "provider": "deepseek", "telemetry": await initializeTelemetryAfterTrust(**kwargs)}


init = {"provider": "deepseek", "call": call, "initializeTelemetryAfterTrust": initializeTelemetryAfterTrust}
default = init


__all__ = ["call", "default", "init", "initializeTelemetryAfterTrust"]
