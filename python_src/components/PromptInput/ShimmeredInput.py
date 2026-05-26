from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def HighlightedInput(*args: Any, **kwargs: Any) -> Any:
    value = str(kwargs.get("value") or (args[0] if args else "") or "")
    return prompt_payload("highlighted_input", value=value, cursor=int(kwargs.get("cursor", len(value)) or 0), shimmer=bool(kwargs.get("shimmer", False)))


__all__ = ["HighlightedInput"]
