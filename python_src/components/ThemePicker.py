from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def ThemePicker(*args: Any, **kwargs: Any) -> dict[str, Any]:
    themes = normalize_items(option(args, kwargs, "themes", ["dark", "light", "system"]), text_key="name")
    selected = str(option(args, kwargs, "selected", scalar_arg(args, "system")) or "system")
    for theme in themes:
        theme["selected"] = str(theme.get("value") or theme.get("name")) == selected
    return component_payload("theme_picker", themes=themes, selected=selected)


__all__ = ["ThemePicker"]
