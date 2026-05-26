from __future__ import annotations

from typing import Any


_PROMPT_OVERLAY: dict[str, Any] = {"value": None, "dialog": None}


async def PromptOverlayProvider(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    if "value" in kwargs:
        _PROMPT_OVERLAY["value"] = kwargs["value"]
    if "dialog" in kwargs:
        _PROMPT_OVERLAY["dialog"] = kwargs["dialog"]
    return {"provider": "deepseek", **_PROMPT_OVERLAY}


async def usePromptOverlay(*_args: Any, **_kwargs: Any) -> Any:
    return _PROMPT_OVERLAY.get("value")


async def usePromptOverlayDialog(*_args: Any, **_kwargs: Any) -> Any:
    return _PROMPT_OVERLAY.get("dialog")


async def useSetPromptOverlay(*_args: Any, **_kwargs: Any):
    async def setter(value: Any = None) -> dict[str, Any]:
        _PROMPT_OVERLAY["value"] = value
        return {"provider": "deepseek", **_PROMPT_OVERLAY}

    return setter


async def useSetPromptOverlayDialog(*_args: Any, **_kwargs: Any):
    async def setter(value: Any = None) -> dict[str, Any]:
        _PROMPT_OVERLAY["dialog"] = value
        return {"provider": "deepseek", **_PROMPT_OVERLAY}

    return setter


__all__ = [
    "PromptOverlayProvider",
    "usePromptOverlay",
    "usePromptOverlayDialog",
    "useSetPromptOverlay",
    "useSetPromptOverlayDialog",
]
