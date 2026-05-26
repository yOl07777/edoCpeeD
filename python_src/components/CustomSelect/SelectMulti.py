from __future__ import annotations

from typing import Any

from python_src.components.CustomSelect._shared import normalize_options, select_payload


async def SelectMulti(*args: Any, **kwargs: Any) -> Any:
    selected = kwargs.get("selected") or kwargs.get("selectedValues") or []
    options = normalize_options(kwargs.get("options") or (args[0] if args else []), selected)
    values = [option["value"] for option in options if option["selected"]]
    return select_payload("select_multi", options=options, selected=values, count=len(values))


__all__ = ["SelectMulti"]
