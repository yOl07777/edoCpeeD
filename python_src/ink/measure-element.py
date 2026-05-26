from __future__ import annotations

import importlib
from typing import Any

measureText = importlib.import_module("python_src.ink.measure-text").measureText


def _text(node: Any) -> str:
    if isinstance(node, str):
        return node
    if isinstance(node, dict):
        if "visibleText" in node:
            return str(node["visibleText"])
        if "text" in node:
            return str(node["text"])
        return "".join(_text(child) for child in node.get("children", []) or [])
    if isinstance(node, (list, tuple)):
        return "".join(_text(child) for child in node)
    return str(node)


def measureElement(*args: Any, **kwargs: Any) -> dict[str, int]:
    node = args[0] if args else kwargs.get("node", "")
    text = _text(node)
    lines = text.splitlines() or [""]
    return {
        "width": max((measureText(line) for line in lines), default=0),
        "height": len(lines),
    }


default = measureElement
_module_migration_placeholder = measureElement
