"""Local `/desktop` command shim."""

from __future__ import annotations

import os
import platform
from typing import Any


def isSupportedPlatform() -> bool:
    system = platform.system().lower()
    machine = platform.machine().lower()
    return system == "darwin" or (system == "windows" and machine in {"amd64", "x86_64"})


def getDesktopHandoffInfo() -> dict[str, Any]:
    product = os.getenv("DEEPCODE_DESKTOP_PRODUCT", "DeepSeek Desktop")
    return {
        "supported": isSupportedPlatform(),
        "product": product,
        "platform": platform.system(),
        "arch": platform.machine(),
        "message": (
            f"Continue this session in {product}."
            if isSupportedPlatform()
            else f"{product} handoff is not supported on this platform."
        ),
    }


async def call(onDone: Any = None, *_args: Any, **_kwargs: Any) -> dict[str, Any] | None:
    info = getDesktopHandoffInfo()
    if callable(onDone):
        try:
            onDone(info["message"], {"display": "system"})
        except TypeError:
            onDone(info["message"])
        return None
    return {"type": "desktop_handoff", **info}
