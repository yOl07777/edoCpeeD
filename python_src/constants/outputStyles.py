"""Output style configuration for the DeepSeek Python runtime."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from python_src.outputStyles.loadOutputStylesDir import clearOutputStyleCaches, getOutputStyleDirStyles
from python_src.utils.plugins.loadPluginOutputStyles import loadPluginOutputStyles
from python_src.utils.settings.settings import getSettings_DEPRECATED

DEFAULT_OUTPUT_STYLE_NAME = "default"

EXPLANATORY_FEATURE_PROMPT = """
## Insights
When useful, provide brief educational explanations about implementation choices before or after code changes. Keep them specific to the codebase and the task at hand.
""".strip()

OUTPUT_STYLE_CONFIG: dict[str, dict[str, Any] | None] = {
    DEFAULT_OUTPUT_STYLE_NAME: None,
    "Explanatory": {
        "name": "Explanatory",
        "source": "built-in",
        "description": "DeepSeek explains implementation choices and codebase patterns",
        "keepCodingInstructions": True,
        "prompt": (
            "You are an interactive CLI tool that helps users with software engineering tasks. "
            "In addition to completing the task, provide clear educational insights when they are useful.\n\n"
            "# Explanatory Style Active\n"
            + EXPLANATORY_FEATURE_PROMPT
        ),
    },
    "Learning": {
        "name": "Learning",
        "source": "built-in",
        "description": "DeepSeek asks for small hands-on contributions when that helps learning",
        "keepCodingInstructions": True,
        "prompt": (
            "You are an interactive CLI tool that helps users with software engineering tasks. "
            "Balance task completion with hands-on learning by asking the user to contribute small, meaningful pieces when appropriate.\n\n"
            "# Learning Style Active\n"
            + EXPLANATORY_FEATURE_PROMPT
        ),
    },
}

_ALL_OUTPUT_STYLES_CACHE: dict[str, dict[str, dict[str, Any] | None]] = {}


async def getAllOutputStyles(cwd: str | os.PathLike[str] | None = None) -> dict[str, dict[str, Any] | None]:
    root = str(Path(cwd or os.getcwd()).resolve())
    if root in _ALL_OUTPUT_STYLES_CACHE:
        return {name: (dict(style) if isinstance(style, dict) else None) for name, style in _ALL_OUTPUT_STYLES_CACHE[root].items()}
    all_styles: dict[str, dict[str, Any] | None] = {name: (dict(style) if isinstance(style, dict) else None) for name, style in OUTPUT_STYLE_CONFIG.items()}
    custom_styles = await getOutputStyleDirStyles(root)
    plugin_styles = await loadPluginOutputStyles()
    groups = [
        plugin_styles,
        [style for style in custom_styles if style.get("source") == "userSettings"],
        [style for style in custom_styles if style.get("source") == "projectSettings"],
        [style for style in custom_styles if style.get("source") == "policySettings"],
    ]
    for styles in groups:
        for style in styles:
            name = str(style["name"])
            all_styles[name] = {
                "name": name,
                "description": style.get("description", ""),
                "prompt": style.get("prompt", ""),
                "source": style.get("source"),
                "keepCodingInstructions": style.get("keepCodingInstructions"),
                "forceForPlugin": style.get("forceForPlugin"),
            }
    _ALL_OUTPUT_STYLES_CACHE[root] = all_styles
    return {name: (dict(style) if isinstance(style, dict) else None) for name, style in all_styles.items()}


async def clearAllOutputStylesCache() -> None:
    _ALL_OUTPUT_STYLES_CACHE.clear()
    await clearOutputStyleCaches()


async def getOutputStyleConfig(cwd: str | os.PathLike[str] | None = None) -> dict[str, Any] | None:
    all_styles = await getAllOutputStyles(cwd)
    forced = [style for style in all_styles.values() if isinstance(style, dict) and style.get("source") == "plugin" and style.get("forceForPlugin") is True]
    if forced:
        return forced[0]
    settings = await getSettings_DEPRECATED(cwd)
    output_style = str(settings.get("outputStyle") or DEFAULT_OUTPUT_STYLE_NAME)
    style = all_styles.get(output_style)
    return dict(style) if isinstance(style, dict) else None


async def hasCustomOutputStyle(cwd: str | os.PathLike[str] | None = None) -> bool:
    settings = await getSettings_DEPRECATED(cwd)
    style = settings.get("outputStyle")
    return style is not None and style != DEFAULT_OUTPUT_STYLE_NAME
