from __future__ import annotations

from typing import Any

from python_src.components.agents._shared import AGENT_COLORS, component_result


async def ColorPicker(*args: Any, **kwargs: Any) -> Any:
    selected = str(kwargs.get("selected") or (args[0] if args else "") or AGENT_COLORS[0])
    return component_result(
        "color_picker",
        colors=[{"name": color, "selected": color == selected} for color in AGENT_COLORS],
        selected=selected,
    )


__all__ = ["ColorPicker"]
