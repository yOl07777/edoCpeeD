from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def PromptInputFooterLeftSide(*args: Any, **kwargs: Any) -> Any:
    return prompt_payload("prompt_input_footer_left", model=kwargs.get("model", "deepseek-chat"), cwd=str(kwargs.get("cwd") or ""), toolsEnabled=bool(kwargs.get("toolsEnabled", True)))


__all__ = ["PromptInputFooterLeftSide"]
