from __future__ import annotations

from typing import Any

from ._nodes import normalize_children, render_node, text_from_children


def _coerce_int(value: Any, default: int, minimum: int = 0) -> int:
    try:
        return max(minimum, int(value))
    except (TypeError, ValueError):
        return default


def ScrollBox(*children: Any, **props: Any) -> dict[str, Any]:
    prop_children = props.pop("children", None)
    node_children = normalize_children(prop_children, *children)
    offset = _coerce_int(props.pop("offset", props.pop("scrollTop", 0)), 0)
    height = _coerce_int(props.pop("height", props.pop("visibleRows", 10)), 10, 1)
    text = props.pop("text", None)
    lines = str(text if text is not None else text_from_children(node_children)).splitlines()
    visible_lines = lines[offset : offset + height]
    return render_node(
        "scroll_box",
        children=node_children,
        offset=offset,
        height=height,
        totalLines=len(lines),
        visibleText="\n".join(visible_lines),
        style=props,
    )


default = ScrollBox
_module_migration_placeholder = ScrollBox
