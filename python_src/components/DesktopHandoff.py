from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def DesktopHandoff(*args: Any, **kwargs: Any) -> Any:
    platform = str(option(args, kwargs, "platform", scalar_arg(args, "windows")))
    url = await getDownloadUrl(platform=platform)
    return component_payload("desktop_handoff", platform=platform, downloadUrl=url, opensBrowser=False)


async def getDownloadUrl(*args: Any, **kwargs: Any) -> Any:
    platform = str(option(args, kwargs, "platform", scalar_arg(args, "windows"))).lower()
    suffix = "mac" if "darwin" in platform or "mac" in platform else "windows" if "win" in platform else "linux"
    return f"https://deepseek.com/download/{suffix}"


__all__ = ["DesktopHandoff", "getDownloadUrl"]
