from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import vim_enabled


async def getNewlineInstructions(*_args: Any, **kwargs: Any) -> Any:
    if kwargs.get("pasteMode", False):
        return "End multiline input with .end on its own line."
    return "Use a trailing backslash to continue on the next line."


async def isNonSpacePrintable(*args: Any, **kwargs: Any) -> Any:
    char = str(kwargs.get("char") or (args[0] if args else "") or "")
    return len(char) == 1 and char.isprintable() and not char.isspace()


async def isVimModeEnabled(*_args: Any, **_kwargs: Any) -> Any:
    return vim_enabled()


__all__ = ["getNewlineInstructions", "isNonSpacePrintable", "isVimModeEnabled"]
