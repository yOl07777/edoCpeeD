"""Non-React interactive helper shims for DeepSeek Code."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Callable

from python_src.bootstrap import state as bootstrap_state


def _message_from_args(args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    if "message" in kwargs:
        return str(kwargs["message"])
    if "error" in kwargs:
        return str(kwargs["error"])
    if args:
        return str(args[0])
    return ""


async def completeOnboarding(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    bootstrap_state.setSessionTrustAccepted(True)
    return {
        "type": "onboarding_complete",
        "provider": "deepseek",
        "completed": True,
        "sessionId": bootstrap_state.getSessionId(),
    }


async def exitWithError(*args: Any, **kwargs: Any) -> dict[str, Any]:
    message = _message_from_args(args, kwargs) or "DeepSeek Code exited with an error."
    return {"type": "exit", "ok": False, "code": int(kwargs.get("code", 1)), "message": message}


async def exitWithMessage(*args: Any, **kwargs: Any) -> dict[str, Any]:
    message = _message_from_args(args, kwargs) or "DeepSeek Code session finished."
    return {"type": "exit", "ok": True, "code": int(kwargs.get("code", 0)), "message": message}


async def getRenderContext(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    cwd = Path(kwargs.get("cwd") or os.getcwd()).resolve()
    return {
        "type": "render_context",
        "provider": "deepseek",
        "cwd": str(cwd),
        "isInteractive": bool(kwargs.get("isInteractive", bootstrap_state.getIsInteractive())),
        "sessionId": bootstrap_state.getSessionId(),
        "model": bootstrap_state.getModelStrings().get("main", os.getenv("DEFAULT_MODEL", "deepseek-chat")),
    }


async def renderAndRun(component: Any = None, *args: Any, **kwargs: Any) -> Any:
    if callable(component):
        result = component(*args, **kwargs)
        if hasattr(result, "__await__"):
            result = await result
        return result
    return {
        "type": "render_result",
        "provider": "deepseek",
        "component": getattr(component, "__name__", str(component or "none")),
        "rendered": False,
    }


async def showDialog(dialog: Any = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    title = kwargs.get("title") or getattr(dialog, "__name__", None) or str(dialog or "dialog")
    return {
        "type": "dialog",
        "provider": "deepseek",
        "title": title,
        "args": [str(arg) for arg in args],
        "message": kwargs.get("message") or "",
        "accepted": bool(kwargs.get("defaultAccepted", True)),
    }


async def showSetupDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    result = await showDialog("setup", *args, **kwargs)
    result["setup"] = True
    return result


async def showSetupScreens(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    screens = kwargs.get("screens") or ["welcome", "api-key", "workspace"]
    return {
        "type": "setup_screens",
        "provider": "deepseek",
        "screens": list(screens),
        "completed": bool(kwargs.get("completed", False)),
    }


__all__ = [
    "completeOnboarding",
    "exitWithError",
    "exitWithMessage",
    "getRenderContext",
    "renderAndRun",
    "showDialog",
    "showSetupDialog",
    "showSetupScreens",
]
