from __future__ import annotations

from typing import Any

from python_src.components.CustomSelect._shared import clamp_index, normalize_options, select_payload


async def useSelectState(*args: Any, **kwargs: Any) -> Any:
    options = normalize_options(kwargs.get("options") or (args[0] if args else []) or [], kwargs.get("selected"))
    index = clamp_index(int(kwargs.get("index", kwargs.get("selectedIndex", 0)) or 0), len(options))
    return select_payload("select_state", options=options, index=index, selected=options[index]["value"] if options else None)


__all__ = ["useSelectState"]
