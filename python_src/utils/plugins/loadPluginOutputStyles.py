"""Plugin output style loader shim."""

from __future__ import annotations

from typing import Any

_PLUGIN_OUTPUT_STYLES: list[dict[str, Any]] = []
_PLUGIN_OUTPUT_STYLE_CACHE: list[dict[str, Any]] | None = None


async def loadPluginOutputStyles() -> list[dict[str, Any]]:
    global _PLUGIN_OUTPUT_STYLE_CACHE
    if _PLUGIN_OUTPUT_STYLE_CACHE is None:
        _PLUGIN_OUTPUT_STYLE_CACHE = [dict(style) for style in _PLUGIN_OUTPUT_STYLES]
    return [dict(style) for style in _PLUGIN_OUTPUT_STYLE_CACHE]


def setPluginOutputStylesForTesting(styles: list[dict[str, Any]]) -> None:
    global _PLUGIN_OUTPUT_STYLE_CACHE
    _PLUGIN_OUTPUT_STYLES.clear()
    _PLUGIN_OUTPUT_STYLES.extend(dict(style) for style in styles)
    _PLUGIN_OUTPUT_STYLE_CACHE = None


async def clearPluginOutputStyleCache() -> None:
    global _PLUGIN_OUTPUT_STYLE_CACHE
    _PLUGIN_OUTPUT_STYLE_CACHE = None
