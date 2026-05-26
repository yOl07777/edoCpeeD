from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


FOOTER_TEMPORARY_STATUS_TIMEOUT = 3000


async def Notifications(*args: Any, **kwargs: Any) -> Any:
    items = kwargs.get("notifications") or (args[0] if args else []) or []
    if isinstance(items, str):
        items = [items]
    return prompt_payload("prompt_notifications", notifications=[str(item) for item in items], count=len(items), timeoutMs=FOOTER_TEMPORARY_STATUS_TIMEOUT)


__all__ = ["FOOTER_TEMPORARY_STATUS_TIMEOUT", "Notifications"]
