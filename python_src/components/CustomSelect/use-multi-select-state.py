from __future__ import annotations

from typing import Any

from python_src.components.CustomSelect._shared import normalize_options, select_payload


async def useMultiSelectState(*args: Any, **kwargs: Any) -> Any:
    options = kwargs.get("options") or (args[0] if args else []) or []
    selected = set(kwargs.get("selected") or [])
    toggle = kwargs.get("toggle")
    if toggle is not None:
        selected.remove(toggle) if toggle in selected else selected.add(toggle)
    rows = normalize_options(options, list(selected))
    return select_payload("multi_select_state", options=rows, selected=[row["value"] for row in rows if row["selected"]])


__all__ = ["useMultiSelectState"]
