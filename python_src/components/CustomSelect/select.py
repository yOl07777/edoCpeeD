from __future__ import annotations

from typing import Any

from python_src.components.CustomSelect._shared import clamp_index, normalize_options, select_payload


async def Select(*args: Any, **kwargs: Any) -> Any:
    options = normalize_options(kwargs.get("options") or (args[0] if args else []), kwargs.get("selected"))
    active_index = clamp_index(int(kwargs.get("activeIndex", kwargs.get("selectedIndex", 0)) or 0), len(options))
    return select_payload("select", options=options, activeIndex=active_index, value=options[active_index]["value"] if options else None)


__all__ = ["Select"]
