from __future__ import annotations

from typing import Any


def _node(value: Any, index: int = 0, selected: str | None = None) -> dict[str, Any]:
    if isinstance(value, dict):
        node_id = str(value.get("id") or value.get("value") or value.get("label") or index)
        label = str(value.get("label") or node_id)
        children = [_node(child, child_index, selected) for child_index, child in enumerate(value.get("children", []))]
    else:
        node_id = str(value)
        label = str(value)
        children = []
    return {"id": node_id, "label": label, "selected": selected == node_id, "children": children}


async def TreeSelect(*args: Any, **kwargs: Any) -> Any:
    items = kwargs.get("items") or (args[0] if args else []) or []
    selected = kwargs.get("selected")
    nodes = [_node(item, index, selected) for index, item in enumerate(items)]
    return {"type": "tree_select", "provider": "deepseek", "nodes": nodes, "count": len(nodes), "selected": selected}


__all__ = ["TreeSelect"]
