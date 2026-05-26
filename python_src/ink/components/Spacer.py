from __future__ import annotations

from typing import Any

from ._nodes import render_node


def Spacer(*args: Any, **props: Any) -> dict[str, Any]:
    size = props.pop("size", args[0] if args else 1)
    axis = props.pop("axis", "vertical")
    try:
        normalized_size = max(0, int(size))
    except (TypeError, ValueError):
        normalized_size = 1
    return render_node("spacer", size=normalized_size, axis=axis, style=props)


default = Spacer
_module_migration_placeholder = Spacer
