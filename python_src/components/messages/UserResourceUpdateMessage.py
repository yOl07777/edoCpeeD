from __future__ import annotations

from typing import Any

from python_src.components.messages._shared import message_payload


async def UserResourceUpdateMessage(*args: Any, **kwargs: Any) -> Any:
    resources = kwargs.get("resources") or (args[0] if args else []) or []
    if isinstance(resources, dict):
        resources = [resources]
    return message_payload("user_resource_update_message", resources=resources, count=len(resources))


__all__ = ["UserResourceUpdateMessage"]
