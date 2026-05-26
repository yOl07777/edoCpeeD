from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def TeleportStash(*args: Any, **kwargs: Any) -> dict[str, Any]:
    files = normalize_items(option(args, kwargs, "files", scalar_arg(args, [])), text_key="path")
    return component_payload("teleport_stash", files=files, count=len(files), stashed=bool(files))


__all__ = ["TeleportStash"]
