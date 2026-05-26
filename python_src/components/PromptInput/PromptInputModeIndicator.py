from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def PromptInputModeIndicator(*args: Any, **kwargs: Any) -> Any:
    mode = str(kwargs.get("mode") or (args[0] if args else "prompt"))
    labels = {"shell": "!", "command": "/", "file": "@", "memory": "#", "help": "?", "prompt": ">"}
    return prompt_payload("prompt_input_mode_indicator", mode=mode, label=labels.get(mode, ">"))


__all__ = ["PromptInputModeIndicator"]
