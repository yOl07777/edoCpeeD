from __future__ import annotations

from typing import Any

from ._nodes import normalize_children, render_node


def Box(*children: Any, **props: Any) -> dict[str, Any]:
    prop_children = props.pop("children", None)
    layout = props.pop("layout", None)
    style = dict(props)
    return render_node(
        "box",
        children=normalize_children(prop_children, *children),
        style=style,
        layout=layout or {},
    )


default = Box
_module_migration_placeholder = Box
