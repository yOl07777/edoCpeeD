from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def TagTabs(*args: Any, **kwargs: Any) -> dict[str, Any]:
    tags = normalize_items(option(args, kwargs, "tags", scalar_arg(args, [])), text_key="label")
    selected = str(option(args, kwargs, "selected", kwargs.get("active", "")) or "")
    for tag in tags:
        value = str(tag.get("value") or tag.get("id") or tag.get("label") or "")
        tag["selected"] = bool(selected and value == selected)
    return component_payload("tag_tabs", tags=tags, selected=selected, count=len(tags))


__all__ = ["TagTabs"]
