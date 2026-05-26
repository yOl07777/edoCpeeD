from __future__ import annotations

from typing import Any

from ._nodes import normalize_children, render_node, text_from_children


def Button(*children: Any, **props: Any) -> dict[str, Any]:
    prop_children = props.pop("children", None)
    node_children = normalize_children(prop_children, *children)
    label = props.pop("label", props.pop("text", None))
    disabled = bool(props.pop("disabled", False))
    focused = bool(props.pop("focused", props.pop("isFocused", False)))
    return render_node(
        "button",
        label=str(label) if label is not None else text_from_children(node_children),
        disabled=disabled,
        focused=focused,
        children=node_children,
        action=props.pop("action", None),
        style=props,
    )


default = Button
_module_migration_placeholder = Button
