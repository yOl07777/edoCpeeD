"""Tiny Ink compatibility shim for Python terminal code."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class InkRoot:
    component: Any = None
    options: dict[str, Any] = field(default_factory=dict)
    frames: list[Any] = field(default_factory=list)
    unmounted: bool = False

    def render(self, component: Any | None = None) -> dict[str, Any]:
        if component is not None:
            self.component = component
        frame = {
            "type": "ink_frame",
            "provider": "deepseek",
            "component": getattr(self.component, "__name__", str(self.component or "none")),
        }
        self.frames.append(frame)
        return frame

    def unmount(self) -> dict[str, Any]:
        self.unmounted = True
        return {"type": "ink_unmount", "provider": "deepseek", "unmounted": True}


async def createRoot(component: Any = None, **kwargs: Any) -> InkRoot:
    return InkRoot(component=component, options=dict(kwargs))


async def render(component: Any = None, **kwargs: Any) -> dict[str, Any]:
    root = await createRoot(component, **kwargs)
    result = root.render()
    result["root"] = root
    return result


__all__ = ["InkRoot", "createRoot", "render"]
