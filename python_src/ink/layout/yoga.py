from __future__ import annotations

from typing import Any

class YogaLayoutNode:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        style = args[0] if args and isinstance(args[0], dict) else kwargs.get("style", {})
        self.args = args
        self.kwargs = kwargs
        self.style = dict(style or {})
        self.children: list[Any] = list(kwargs.get("children", []))
        self.layout = {
            "x": int(self.style.get("x", 0) or 0),
            "y": int(self.style.get("y", 0) or 0),
            "width": int(self.style.get("width", 0) or 0),
            "height": int(self.style.get("height", 0) or 0),
        }

    def insertChild(self, child: Any, index: int | None = None) -> None:
        if index is None:
            self.children.append(child)
        else:
            self.children.insert(index, child)

    def removeChild(self, child: Any) -> None:
        if child in self.children:
            self.children.remove(child)

    def calculateLayout(self, width: int | None = None, height: int | None = None) -> dict[str, int]:
        if width is not None:
            self.layout["width"] = int(width)
        if height is not None:
            self.layout["height"] = int(height)
        return dict(self.layout)

    def getComputedLayout(self) -> dict[str, int]:
        return dict(self.layout)

async def createYogaLayoutNode(*args: Any, **kwargs: Any) -> Any:
    return YogaLayoutNode(*args, **kwargs)
