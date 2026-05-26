"""Load output styles from markdown directories."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from python_src.utils.frontmatterParser import coerceDescriptionToString
from python_src.utils.markdownConfigLoader import clearMarkdownConfigLoaderCache, extractDescriptionFromMarkdown, loadMarkdownFilesForSubdir
from python_src.utils.plugins.loadPluginOutputStyles import clearPluginOutputStyleCache

_OUTPUT_STYLE_CACHE: dict[str, list[dict[str, Any]]] = {}


def _parse_optional_bool(value: Any) -> bool | None:
    if value is True or value == "true":
        return True
    if value is False or value == "false":
        return False
    return None


async def getOutputStyleDirStyles(cwd: str) -> list[dict[str, Any]]:
    key = str(Path(cwd).resolve())
    if key in _OUTPUT_STYLE_CACHE:
        return [dict(style) for style in _OUTPUT_STYLE_CACHE[key]]
    styles: list[dict[str, Any]] = []
    for item in await loadMarkdownFilesForSubdir("output-styles", cwd):
        path = Path(item["filePath"])
        style_name = path.stem
        frontmatter = item.get("frontmatter") or {}
        content = str(item.get("content") or "").strip()
        name = str(frontmatter.get("name") or style_name)
        description = coerceDescriptionToString(frontmatter.get("description"), style_name) or extractDescriptionFromMarkdown(content, f"Custom {style_name} output style")
        styles.append(
            {
                "name": name,
                "description": description,
                "prompt": content,
                "source": item.get("source", "projectSettings"),
                "keepCodingInstructions": _parse_optional_bool(frontmatter.get("keep-coding-instructions")),
            }
        )
    _OUTPUT_STYLE_CACHE[key] = styles
    return [dict(style) for style in styles]


async def clearOutputStyleCaches() -> None:
    _OUTPUT_STYLE_CACHE.clear()
    clearMarkdownConfigLoaderCache()
    await clearPluginOutputStyleCache()
