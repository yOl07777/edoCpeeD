from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def OutputStylePicker(*args: Any, **kwargs: Any) -> Any:
    selected = str(option(args, kwargs, "selected", option(args, kwargs, "style", scalar_arg(args, "default"))))
    styles = normalize_items(option(args, kwargs, "styles", ["default", "brief", "explanatory", "learning"]), text_key="name")
    for style in styles:
        style["selected"] = style["name"] == selected
    return component_payload("output_style_picker", selected=selected, styles=styles)


__all__ = ["OutputStylePicker"]
