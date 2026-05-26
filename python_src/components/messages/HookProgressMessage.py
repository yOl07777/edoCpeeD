from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def HookProgressMessage(*args: Any, **kwargs: Any) -> Any:
    hook = str(kwargs.get("hook") or kwargs.get("name") or (args[0] if args else "hook"))
    status = str(kwargs.get("status") or "running")
    return message_payload("hook_progress_message", hook=hook, status=status, message=f"{hook}: {status}")


__all__ = ["HookProgressMessage"]
