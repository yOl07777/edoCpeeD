from __future__ import annotations

from typing import Any

from ._nodes import normalize_children, render_node


TerminalFocusContext: dict[str, Any] = {"isFocused": True, "provider": "deepseek"}


async def TerminalFocusProvider(*args: Any, **kwargs: Any) -> Any:
    prop_children = kwargs.pop("children", None)
    focused = bool(kwargs.pop("focused", kwargs.pop("isFocused", True)))
    return render_node(
        "terminal_focus_provider",
        context={"provider": "deepseek", "isFocused": focused},
        children=normalize_children(prop_children, *args),
        props=kwargs,
    )


default = TerminalFocusProvider
