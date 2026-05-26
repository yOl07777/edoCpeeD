from __future__ import annotations

from typing import Any

from ._nodes import normalize_children, render_node


async def AlternateScreen(*args: Any, **kwargs: Any) -> Any:
    prop_children = kwargs.pop("children", None)
    enabled = bool(kwargs.pop("enabled", True))
    return render_node(
        "alternate_screen",
        enabled=enabled,
        enter="\x1b[?1049h" if enabled else "",
        exit="\x1b[?1049l" if enabled else "",
        children=normalize_children(prop_children, *args),
        props=kwargs,
    )


default = AlternateScreen
