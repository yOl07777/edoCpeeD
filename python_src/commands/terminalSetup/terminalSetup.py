"""Terminal setup command shim."""

from __future__ import annotations

import os
from typing import Any, Callable

from python_src.utils.config import getGlobalConfig, saveGlobalConfig


def _emit(onDone: Callable[..., Any] | None, message: str, options: dict[str, Any] | None = None) -> None:
    if not callable(onDone):
        return
    try:
        onDone(message, options) if options is not None else onDone(message)
    except TypeError:
        onDone(message)


async def getNativeCSIuTerminalDisplayName(term_program: str | None = None) -> str | None:
    program = (term_program or os.getenv("TERM_PROGRAM") or "").lower()
    if "iterm" in program:
        return "iTerm2"
    if "vscode" in program:
        return "VS Code"
    if "wezterm" in program:
        return "WezTerm"
    if "windows_terminal" in program or os.getenv("WT_SESSION"):
        return "Windows Terminal"
    return None


async def hasUsedBackslashReturn() -> bool:
    return bool((await getGlobalConfig()).get("hasUsedBackslashReturn"))


async def markBackslashReturnUsed() -> dict[str, Any]:
    return await saveGlobalConfig({"hasUsedBackslashReturn": True})


async def isShiftEnterKeyBindingInstalled() -> bool:
    return bool((await getGlobalConfig()).get("shiftEnterKeyBindingInstalled"))


async def setupTerminal() -> dict[str, Any]:
    display = await getNativeCSIuTerminalDisplayName()
    config = await saveGlobalConfig({"shiftEnterKeyBindingInstalled": True, "terminalSetupDisplayName": display})
    return {"installed": True, "displayName": display, "config": config}


async def shouldOfferTerminalSetup() -> bool:
    return not await isShiftEnterKeyBindingInstalled()


async def call(onDone: Callable[..., Any] | None = None, _context: Any | None = None, args: str | None = None) -> dict[str, Any]:
    action = (args or "status").strip().lower() or "status"
    if action in {"install", "setup", "enable"}:
        result = await setupTerminal()
        _emit(onDone, "Terminal key binding setup recorded.", {"display": "system"})
        return {"type": "terminal_setup", "action": "install", **result}
    if action in {"mark-backslash-return", "backslash-return"}:
        config = await markBackslashReturnUsed()
        return {"type": "terminal_setup", "action": "mark-backslash-return", "config": config}
    return {
        "type": "terminal_setup",
        "action": "status",
        "displayName": await getNativeCSIuTerminalDisplayName(),
        "installed": await isShiftEnterKeyBindingInstalled(),
        "shouldOffer": await shouldOfferTerminalSetup(),
        "hasUsedBackslashReturn": await hasUsedBackslashReturn(),
    }
