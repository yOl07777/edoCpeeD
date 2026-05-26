from __future__ import annotations

from typing import Any


async def hasFrictionSignal(signals: list[Any] | None = None, *_args: Any, **kwargs: Any) -> bool:
    items = list(kwargs.get("signals", signals or []))
    return any(str(item).lower() in {"error", "crash", "slow", "blocked", "failed"} for item in items)


async def isSessionContainerCompatible(*_args: Any, **kwargs: Any) -> bool:
    return str(kwargs.get("container", "terminal")).lower() in {"terminal", "desktop", "local"}


async def useIssueFlagBanner(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    visible = await hasFrictionSignal(kwargs.get("signals", [])) and await isSessionContainerCompatible(container=kwargs.get("container", "terminal"))
    return {"provider": "deepseek", "visible": visible, "message": "Report this DeepSeek Code issue" if visible else ""}


__all__ = ["hasFrictionSignal", "isSessionContainerCompatible", "useIssueFlagBanner"]
