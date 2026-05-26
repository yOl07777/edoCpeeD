from __future__ import annotations

from typing import Any

from python_src.components.CustomSelect._shared import select_payload


async def useSelectInput(*args: Any, **kwargs: Any) -> Any:
    key = str(kwargs.get("key") or (args[0] if args else "") or "")
    mapping = {"up": -1, "k": -1, "down": 1, "j": 1, "enter": 0, "space": 0}
    return select_payload("select_input", key=key, delta=mapping.get(key, 0), submit=key == "enter", toggle=key == "space")


__all__ = ["useSelectInput"]
