"""Supported local ConfigTool settings."""

from __future__ import annotations

from typing import Any

SUPPORTED_SETTINGS: dict[str, dict[str, Any]] = {
    "model": {
        "key": "model",
        "path": "model",
        "type": "string",
        "description": "Default model name for DeepSeek Code.",
        "options": ["deepseek-chat", "deepseek-coder"],
    },
    "stream": {
        "key": "stream",
        "path": "stream",
        "type": "boolean",
        "description": "Whether terminal responses stream by default.",
        "options": [True, False],
    },
    "tools.enabled": {
        "key": "tools.enabled",
        "path": "tools.enabled",
        "type": "boolean",
        "description": "Whether local workspace tools are enabled.",
        "options": [True, False],
    },
    "max_tokens": {
        "key": "max_tokens",
        "path": "max_tokens",
        "type": "integer",
        "description": "Optional maximum output token count.",
        "options": [],
    },
    "temperature": {
        "key": "temperature",
        "path": "temperature",
        "type": "number",
        "description": "Optional sampling temperature.",
        "options": [],
    },
}


def _key(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    return str(kwargs.get("key") or kwargs.get("setting") or (args[0] if args else ""))


async def getAllKeys(*args: Any, **kwargs: Any) -> list[str]:
    return sorted(SUPPORTED_SETTINGS)


async def getConfig(*args: Any, **kwargs: Any) -> dict[str, Any] | None:
    key = _key(args, kwargs)
    return SUPPORTED_SETTINGS.get(key)


async def getOptionsForSetting(*args: Any, **kwargs: Any) -> list[Any]:
    config = await getConfig(*args, **kwargs)
    return list(config.get("options", [])) if config else []


async def getPath(*args: Any, **kwargs: Any) -> str | None:
    config = await getConfig(*args, **kwargs)
    return str(config.get("path")) if config else None


async def isSupported(*args: Any, **kwargs: Any) -> bool:
    return _key(args, kwargs) in SUPPORTED_SETTINGS


__all__ = [
    "SUPPORTED_SETTINGS",
    "getAllKeys",
    "getConfig",
    "getOptionsForSetting",
    "getPath",
    "isSupported",
]
