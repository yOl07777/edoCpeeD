from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def PromptInputQueuedCommands(*args: Any, **kwargs: Any) -> Any:
    commands = kwargs.get("commands") or (args[0] if args else []) or []
    return prompt_payload("prompt_input_queued_commands", commands=[str(command) for command in commands], count=len(commands))


__all__ = ["PromptInputQueuedCommands"]
