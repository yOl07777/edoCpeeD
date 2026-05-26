"""Small render-node helpers for migrated Ink component shims."""

from __future__ import annotations

from typing import Any


def normalize_children(children: Any = None, *extra: Any) -> list[Any]:
    values: list[Any] = []
    if children is not None:
        if isinstance(children, (list, tuple)):
            values.extend(children)
        else:
            values.append(children)
    for value in extra:
        if value is None:
            continue
        if isinstance(value, (list, tuple)):
            values.extend(value)
        else:
            values.append(value)
    return values


def text_from_children(children: Any = None, *extra: Any) -> str:
    parts: list[str] = []
    for child in normalize_children(children, *extra):
        if isinstance(child, dict):
            if "text" in child:
                parts.append(str(child["text"]))
            elif "children" in child:
                parts.append(text_from_children(child["children"]))
            continue
        parts.append(str(child))
    return "".join(parts)


def render_node(kind: str, **payload: Any) -> dict[str, Any]:
    return {"provider": "deepseek", "type": kind, **payload}
