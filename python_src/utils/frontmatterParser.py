"""Frontmatter parser for markdown configuration files."""

from __future__ import annotations

import re
from typing import Any

from .yaml import parseYaml

FRONTMATTER_REGEX = re.compile(r"^---\s*\n([\s\S]*?)---\s*\n?")
YAML_SPECIAL_CHARS = re.compile(r"[{}\[\]*&#!|>%@`]|: ")
FRONTMATTER_SHELLS = {"bash", "powershell"}


def _quote_problematic_values(frontmatter_text: str) -> str:
    lines: list[str] = []
    for line in frontmatter_text.splitlines():
        match = re.match(r"^([a-zA-Z_-]+):\s+(.+)$", line)
        if not match:
            lines.append(line)
            continue
        key, value = match.groups()
        if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
            lines.append(line)
        elif YAML_SPECIAL_CHARS.search(value):
            escaped = value.replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key}: "{escaped}"')
        else:
            lines.append(line)
    return "\n".join(lines)


def parseFrontmatter(markdown: str, sourcePath: str | None = None) -> dict[str, Any]:
    match = FRONTMATTER_REGEX.match(markdown)
    if not match:
        return {"frontmatter": {}, "content": markdown}
    frontmatter_text = match.group(1) or ""
    content = markdown[match.end() :]
    frontmatter: dict[str, Any] = {}
    for candidate in (frontmatter_text, _quote_problematic_values(frontmatter_text)):
        try:
            parsed = parseYaml(candidate)
            if isinstance(parsed, dict):
                frontmatter = parsed
                break
        except Exception:
            continue
    return {"frontmatter": frontmatter, "content": content}


def _expand_braces(pattern: str) -> list[str]:
    match = re.match(r"^([^{]*)\{([^}]+)\}(.*)$", pattern)
    if not match:
        return [pattern]
    prefix, alternatives, suffix = match.groups()
    expanded: list[str] = []
    for part in alternatives.split(","):
        expanded.extend(_expand_braces(prefix + part.strip() + suffix))
    return expanded


def splitPathInFrontmatter(input: str | list[str] | Any) -> list[str]:
    if isinstance(input, list):
        result: list[str] = []
        for item in input:
            result.extend(splitPathInFrontmatter(item))
        return result
    if not isinstance(input, str):
        return []
    parts: list[str] = []
    current = ""
    brace_depth = 0
    for char in input:
        if char == "{":
            brace_depth += 1
            current += char
        elif char == "}":
            brace_depth -= 1
            current += char
        elif char == "," and brace_depth == 0:
            if current.strip():
                parts.append(current.strip())
            current = ""
        else:
            current += char
    if current.strip():
        parts.append(current.strip())
    result: list[str] = []
    for part in parts:
        result.extend(_expand_braces(part))
    return [part for part in result if part]


def parsePositiveIntFromFrontmatter(value: Any) -> int | None:
    if value is None:
        return None
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return None
    return parsed if parsed > 0 else None


def coerceDescriptionToString(value: Any, componentName: str | None = None, pluginName: str | None = None) -> str | None:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        return stripped or None
    if isinstance(value, (int, float, bool)):
        return str(value)
    return None


def parseBooleanFrontmatter(value: Any) -> bool:
    return value is True or value == "true"


def parseShellFrontmatter(value: Any, source: str = "") -> str | None:
    if value is None:
        return None
    normalized = str(value).strip().lower()
    if not normalized:
        return None
    return normalized if normalized in FRONTMATTER_SHELLS else None
