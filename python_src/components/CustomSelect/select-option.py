from __future__ import annotations

from typing import Any

from python_src.components.CustomSelect._shared import normalize_option, select_payload


async def SelectOption(*args: Any, **kwargs: Any) -> Any:
    option = normalize_option(kwargs.get("option") or (args[0] if args else ""), int(kwargs.get("index", 0) or 0), bool(kwargs.get("selected", False)))
    return select_payload("select_option", option=option, marker=">" if kwargs.get("active", False) else " ")


__all__ = ["SelectOption"]
