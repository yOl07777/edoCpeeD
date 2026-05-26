from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def PromptInputStashNotice(*args: Any, **kwargs: Any) -> Any:
    count = int(kwargs.get("count", args[0] if args else 0) or 0)
    return prompt_payload("prompt_input_stash_notice", count=count, visible=count > 0, message=f"{count} stashed input item(s)")


__all__ = ["PromptInputStashNotice"]
