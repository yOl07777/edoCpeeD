from __future__ import annotations

from typing import Any

from python_src.components.CustomSelect._shared import clamp_index, normalize_option, normalize_options, select_payload


async def createSelectState(options: Any = None, selectedIndex: int = 0, selected: Any = None, *_args: Any, **_kwargs: Any) -> dict[str, Any]:
    rows = normalize_options(options or [], selected)
    active = clamp_index(int(selectedIndex or 0), len(rows))
    return select_payload("custom_select_state", options=rows, activeIndex=active, active=rows[active] if rows else None)


default = {"provider": "deepseek", "component": "CustomSelect", "createSelectState": createSelectState}


__all__ = ["clamp_index", "createSelectState", "default", "normalize_option", "normalize_options", "select_payload"]
