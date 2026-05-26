from __future__ import annotations

from typing import Any


ModalContext: dict[str, Any] = {"inside": False, "width": 80, "height": 24, "scrollTop": 0}


async def useIsInsideModal(*_args: Any, **kwargs: Any) -> bool:
    if "inside" in kwargs:
        ModalContext["inside"] = bool(kwargs["inside"])
    return bool(ModalContext.get("inside"))


async def useModalOrTerminalSize(*_args: Any, **kwargs: Any) -> dict[str, int]:
    width = int(kwargs.get("width", ModalContext.get("width", 80)) or 80)
    height = int(kwargs.get("height", ModalContext.get("height", 24)) or 24)
    ModalContext.update({"width": width, "height": height})
    return {"width": width, "height": height}


async def useModalScrollRef(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    if "scrollTop" in kwargs:
        ModalContext["scrollTop"] = int(kwargs["scrollTop"])
    return {"current": {"scrollTop": int(ModalContext.get("scrollTop", 0))}}


__all__ = ["ModalContext", "useIsInsideModal", "useModalOrTerminalSize", "useModalScrollRef"]
