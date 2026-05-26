from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import mode_from_text, prompt_payload


async def PromptInput(*args: Any, **kwargs: Any) -> Any:
    value = str(kwargs.get("value") or kwargs.get("input") or (args[0] if args else "") or "")
    mode = kwargs.get("mode") or mode_from_text(value)
    return prompt_payload("prompt_input", value=value, mode=mode, multiline=bool(kwargs.get("multiline", False)), disabled=bool(kwargs.get("disabled", False)))


__all__ = ["PromptInput"]
