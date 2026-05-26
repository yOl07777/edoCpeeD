from __future__ import annotations

from typing import Any


class FocusManager:
    def __init__(self, root: Any = None, *args: Any, **kwargs: Any) -> None:
        self.root = root
        self.items: list[Any] = []
        self.index = -1

    def register(self, item: Any) -> Any:
        self.items.append(item)
        if self.index < 0:
            self.index = 0
        return item

    def unregister(self, item: Any) -> bool:
        if item in self.items:
            self.items.remove(item)
            self.index = min(self.index, len(self.items) - 1)
            return True
        return False

    def focusNext(self) -> Any:
        if not self.items:
            return None
        self.index = (self.index + 1) % len(self.items)
        return self.items[self.index]

    def focusPrevious(self) -> Any:
        if not self.items:
            return None
        self.index = (self.index - 1) % len(self.items)
        return self.items[self.index]

    def focused(self) -> Any:
        return self.items[self.index] if 0 <= self.index < len(self.items) else None


_root_node: Any = None
_focus_manager = FocusManager()


async def getFocusManager(*args: Any, **kwargs: Any) -> Any:
    global _focus_manager
    if args or "root" in kwargs:
        _focus_manager.root = args[0] if args else kwargs.get("root")
    return _focus_manager


async def getRootNode(*args: Any, **kwargs: Any) -> Any:
    global _root_node
    if args or "root" in kwargs:
        _root_node = args[0] if args else kwargs.get("root")
    return _root_node
