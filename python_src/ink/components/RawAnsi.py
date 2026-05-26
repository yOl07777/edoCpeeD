from __future__ import annotations

from typing import Any

from ._nodes import render_node


async def RawAnsi(*args: Any, **kwargs: Any) -> Any:
    value = kwargs.pop("value", kwargs.pop("ansi", args[0] if args else ""))
    return render_node("raw_ansi", value=str(value), props=kwargs)


default = RawAnsi
