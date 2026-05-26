from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def PromptInputFooter(*args: Any, **kwargs: Any) -> Any:
    mode = str(kwargs.get("mode") or (args[0] if args else "prompt"))
    return prompt_payload("prompt_input_footer", mode=mode, hints=kwargs.get("hints") or ["Enter to send", "Shift+Enter for newline"], status=kwargs.get("status"))


__all__ = ["PromptInputFooter"]
