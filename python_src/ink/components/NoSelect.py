from __future__ import annotations

from typing import Any

from ._nodes import normalize_children, render_node


async def NoSelect(*args: Any, **kwargs: Any) -> Any:
    prop_children = kwargs.pop("children", None)
    return render_node("no_select", children=normalize_children(prop_children, *args), props=kwargs)


default = NoSelect
