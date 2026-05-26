"""Sandbox routing decision for migrated bash tooling."""

from __future__ import annotations

import os
from typing import Any

from .destructiveCommandWarning import getDestructiveCommandWarning
from .readOnlyValidation import isCommandSafeViaFlagParsing


async def shouldUseSandbox(*args: Any, **kwargs: Any) -> bool:
    command = str(kwargs.get("command") or (args[0] if args else ""))
    mode = str(kwargs.get("mode") or os.getenv("DEEPCODE_BASH_SANDBOX", "auto")).lower()
    if mode in {"0", "false", "off", "never", "none"}:
        return False
    if mode in {"1", "true", "on", "always"}:
        return True
    if getDestructiveCommandWarning(command):
        return True
    return not isCommandSafeViaFlagParsing(command)


__all__ = ["shouldUseSandbox"]
