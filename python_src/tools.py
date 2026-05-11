from __future__ import annotations

from typing import Any

from python_src.tools.runtime import DEFAULT_TOOLS


TOOL_PRESETS = ["default"]


def parseToolPreset(preset: str) -> str | None:
    preset = preset.lower()
    return preset if preset in TOOL_PRESETS else None


def getToolsForDefaultPreset() -> list[str]:
    return [tool.name for tool in DEFAULT_TOOLS]


def getAllBaseTools() -> list[Any]:
    return list(DEFAULT_TOOLS)


def getTools(*args: Any, **kwargs: Any) -> list[Any]:
    return getAllBaseTools()


def getMergedTools(*args: Any, **kwargs: Any) -> list[Any]:
    return getAllBaseTools()


def assembleToolPool(*args: Any, **kwargs: Any) -> list[Any]:
    return getAllBaseTools()


def filterToolsByDenyRules(tools: list[Any], *args: Any, **kwargs: Any) -> list[Any]:
    return tools
