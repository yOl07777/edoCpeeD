from __future__ import annotations

from typing import Any

from ._nodes import render_node


def Newline(*args: Any, **props: Any) -> dict[str, Any]:
    count = props.pop("count", args[0] if args else 1)
    try:
        normalized_count = max(1, int(count))
    except (TypeError, ValueError):
        normalized_count = 1
    return render_node("newline", count=normalized_count, text="\n" * normalized_count)


default = Newline
_module_migration_placeholder = Newline
