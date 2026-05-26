from __future__ import annotations

from typing import Any

from python_src.components.hooks._shared import hook_payload, normalize_hook


async def PromptDialog(*args: Any, **kwargs: Any) -> Any:
    hook = normalize_hook(kwargs.get("hook") or (args[0] if args else None), **kwargs)
    return hook_payload(
        "hook_prompt_dialog",
        hook=hook,
        prompt=hook["command"],
        valid=bool(hook["command"].strip()),
        title=f"{hook['event']} hook command",
    )


__all__ = ["PromptDialog"]
