from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any


def getEmptyToolPermissionContext() -> dict[str, Any]:
    return {
        "mode": "default",
        "additionalWorkingDirectories": {},
        "alwaysAllowRules": {},
        "alwaysDenyRules": {},
        "alwaysAskRules": {},
        "isBypassPermissionsModeAvailable": False,
    }


async def _default_check_permissions(input: dict[str, Any], _ctx: Any = None) -> dict[str, Any]:
    return {"behavior": "allow", "updatedInput": input}


def _default_user_facing_name(definition: dict[str, Any]) -> Callable[..., str]:
    return lambda *_args, **_kwargs: str(definition.get("name", ""))


def buildTool(definition: dict[str, Any] | Any) -> dict[str, Any]:
    if not isinstance(definition, dict):
        definition = vars(definition).copy()
    tool = {
        "isEnabled": lambda *_args, **_kwargs: True,
        "isConcurrencySafe": lambda *_args, **_kwargs: False,
        "isReadOnly": lambda *_args, **_kwargs: False,
        "isDestructive": lambda *_args, **_kwargs: False,
        "checkPermissions": _default_check_permissions,
        "toAutoClassifierInput": lambda *_args, **_kwargs: "",
        "userFacingName": _default_user_facing_name(definition),
    }
    tool.update(definition)
    return tool


def filterToolProgressMessages(progressMessagesForMessage: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        msg
        for msg in progressMessagesForMessage
        if not isinstance(msg.get("data"), dict) or msg["data"].get("type") != "hook_progress"
    ]


def toolMatchesName(tool: dict[str, Any] | Any, name: str) -> bool:
    tool_name = tool.get("name") if isinstance(tool, dict) else getattr(tool, "name", None)
    aliases = tool.get("aliases", []) if isinstance(tool, dict) else getattr(tool, "aliases", [])
    return tool_name == name or name in (aliases or [])


def findToolByName(tools: Iterable[dict[str, Any] | Any], name: str) -> dict[str, Any] | Any | None:
    return next((tool for tool in tools if toolMatchesName(tool, name)), None)
