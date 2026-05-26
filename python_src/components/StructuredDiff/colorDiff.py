from __future__ import annotations

from typing import Any


async def getColorModuleUnavailableReason(*_args: Any, **_kwargs: Any) -> str | None:
    return None


async def getSyntaxTheme(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    name = kwargs.get("name") or kwargs.get("theme") or "deepseek-terminal"
    return {
        "name": name,
        "added": "green",
        "removed": "red",
        "context": "default",
        "header": "cyan",
    }


async def expectColorDiff(diff: str = "", *_args: Any, **_kwargs: Any) -> dict[str, Any]:
    lines = str(diff or "").splitlines()
    return {
        "type": "color_diff",
        "provider": "deepseek",
        "available": True,
        "lines": lines,
        "added": sum(1 for line in lines if line.startswith("+") and not line.startswith("+++")),
        "removed": sum(1 for line in lines if line.startswith("-") and not line.startswith("---")),
    }


async def expectColorFile(path: str = "", content: str = "", *_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return {
        "type": "color_file",
        "provider": "deepseek",
        "path": path,
        "content": content,
        "lineCount": len(str(content or "").splitlines()),
    }


__all__ = ["expectColorDiff", "expectColorFile", "getColorModuleUnavailableReason", "getSyntaxTheme"]
