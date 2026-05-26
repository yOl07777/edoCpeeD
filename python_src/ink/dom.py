from __future__ import annotations

from typing import Any


def createNode(type: str = "node", **props: Any) -> dict[str, Any]:
    return {"provider": "deepseek", "type": type, "props": props, "style": {}, "children": [], "parent": None, "dirty": True}


def createTextNode(text: str = "") -> dict[str, Any]:
    return createNode("text", text=text)


def appendChildNode(parent: dict[str, Any], child: dict[str, Any]) -> dict[str, Any]:
    parent.setdefault("children", []).append(child)
    child["parent"] = parent
    markDirty(parent)
    return child


def insertBeforeNode(parent: dict[str, Any], child: dict[str, Any], before: dict[str, Any] | None = None) -> dict[str, Any]:
    children = parent.setdefault("children", [])
    index = children.index(before) if before in children else len(children)
    children.insert(index, child)
    child["parent"] = parent
    markDirty(parent)
    return child


def removeChildNode(parent: dict[str, Any], child: dict[str, Any]) -> bool:
    children = parent.setdefault("children", [])
    if child in children:
        children.remove(child)
        child["parent"] = None
        markDirty(parent)
        return True
    return False


def setAttribute(node: dict[str, Any], key: str, value: Any) -> dict[str, Any]:
    node.setdefault("props", {})[key] = value
    markDirty(node)
    return node


def setStyle(node: dict[str, Any], style: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    node.setdefault("style", {}).update(style or {}, **kwargs)
    markDirty(node)
    return node


def setTextStyles(node: dict[str, Any], style: dict[str, Any] | None = None) -> dict[str, Any]:
    return setStyle(node, style or {})


def setTextNodeValue(node: dict[str, Any], value: str) -> dict[str, Any]:
    node.setdefault("props", {})["text"] = str(value)
    markDirty(node)
    return node


def markDirty(node: dict[str, Any]) -> dict[str, Any]:
    node["dirty"] = True
    return node


def clearYogaNodeReferences(node: dict[str, Any]) -> dict[str, Any]:
    node.pop("yogaNode", None)
    for child in node.get("children", []) or []:
        clearYogaNodeReferences(child)
    return node


def scheduleRenderFrom(node: dict[str, Any]) -> dict[str, Any]:
    return markDirty(node)


async def findOwnerChainAtRow(*args: Any, **kwargs: Any) -> Any:
    node = args[0] if args else kwargs.get("node")
    row = int(args[1] if len(args) > 1 else kwargs.get("row", 0))
    chain: list[dict[str, Any]] = []

    def walk(current: dict[str, Any]) -> bool:
        layout = current.get("layout", {})
        top = int(layout.get("top", layout.get("y", 0)))
        height = int(layout.get("height", 1))
        if top <= row < top + height:
            chain.append(current)
            for child in current.get("children", []) or []:
                if walk(child):
                    return True
            return True
        return False

    if isinstance(node, dict):
        walk(node)
    return chain
