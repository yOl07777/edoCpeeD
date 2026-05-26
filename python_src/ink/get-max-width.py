from __future__ import annotations

import importlib
from typing import Any

measureElement = importlib.import_module("python_src.ink.measure-element").measureElement


def getMaxWidth(*args: Any, **kwargs: Any) -> int:
    nodes = args[0] if args else kwargs.get("nodes", [])
    if not isinstance(nodes, (list, tuple)):
        nodes = [nodes]
    return max((measureElement(node)["width"] for node in nodes), default=0)


default = getMaxWidth
_module_migration_placeholder = getMaxWidth
