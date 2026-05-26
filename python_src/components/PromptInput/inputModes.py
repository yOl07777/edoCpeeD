from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import MODE_PREFIXES, mode_from_text, strip_mode_prefix


async def isInputModeCharacter(*args: Any, **kwargs: Any) -> Any:
    char = str(kwargs.get("char") or (args[0] if args else "") or "")[:1]
    return char in MODE_PREFIXES


async def getModeFromInput(*args: Any, **kwargs: Any) -> Any:
    text = str(kwargs.get("input") or (args[0] if args else "") or "")
    return mode_from_text(text)


async def getValueFromInput(*args: Any, **kwargs: Any) -> Any:
    text = str(kwargs.get("input") or (args[0] if args else "") or "")
    return strip_mode_prefix(text)


async def prependModeCharacterToInput(*args: Any, **kwargs: Any) -> Any:
    mode = str(kwargs.get("mode") or (args[0] if args else "prompt"))
    text = str(kwargs.get("input") or (args[1] if len(args) > 1 else "") or "")
    prefix = next((key for key, value in MODE_PREFIXES.items() if value == mode), "")
    return text if not prefix or text.startswith(prefix) else prefix + text


__all__ = ["getModeFromInput", "getValueFromInput", "isInputModeCharacter", "prependModeCharacterToInput"]
