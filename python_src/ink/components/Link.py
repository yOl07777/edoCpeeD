from __future__ import annotations

from typing import Any

from ._nodes import normalize_children, render_node, text_from_children


def Link(*children: Any, **props: Any) -> dict[str, Any]:
    url = props.pop("url", props.pop("href", ""))
    explicit_text = props.pop("text", None)
    prop_children = props.pop("children", None)
    node_children = normalize_children(prop_children, *children)
    text = str(explicit_text) if explicit_text is not None else text_from_children(node_children)
    fallback = f"{text} ({url})" if url else text
    return render_node(
        "link",
        text=text,
        url=str(url),
        fallback=fallback,
        children=node_children,
        style=props,
    )


default = Link
_module_migration_placeholder = Link
