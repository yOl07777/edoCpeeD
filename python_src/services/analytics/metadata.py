"""Telemetry metadata helpers with conservative local sanitization."""

from __future__ import annotations

import os
import re
import shlex
from pathlib import Path
from typing import Any

from python_src.services.mcp.mcpStringUtils import mcpInfoFromString

_SAFE_KEYS = {"path", "file_path", "pattern", "command", "query", "url", "name", "tool", "cwd"}
_PATH_RE = re.compile(r"(?P<path>[\w./\\-]+\.(?P<ext>[A-Za-z0-9]{1,12}))")


async def getFileExtensionForAnalytics(path: str | Path | None) -> str | None:
    suffix = Path(str(path or "")).suffix.lower().lstrip(".")
    return suffix or None


async def getFileExtensionsFromBashCommand(command: str) -> list[str]:
    extensions: list[str] = []
    for match in _PATH_RE.finditer(command or ""):
        ext = match.group("ext").lower()
        if ext not in extensions:
            extensions.append(ext)
    return extensions


async def sanitizeToolNameForAnalytics(tool_name: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.:-]+", "_", str(tool_name or "")).strip("_")
    return value or "unknown"


async def extractMcpToolDetails(tool_name: str) -> dict[str, Any] | None:
    info = await mcpInfoFromString(tool_name)
    if not info.get("isMcp"):
        return None
    return {"server": info.get("serverName"), "tool": info.get("toolName")}


async def mcpToolDetailsForAnalytics(tool_name: str) -> dict[str, Any]:
    return await extractMcpToolDetails(tool_name) or {}


async def extractSkillName(tool_input: dict[str, Any] | str | None) -> str | None:
    if isinstance(tool_input, dict):
        for key in ("skill", "skillName", "name"):
            if tool_input.get(key):
                return str(tool_input[key])
    if isinstance(tool_input, str):
        return tool_input.strip() or None
    return None


async def isAnalyticsToolDetailsLoggingEnabled(config: dict[str, Any] | None = None) -> bool:
    config = config or {}
    if "analyticsToolDetailsLoggingEnabled" in config:
        return bool(config["analyticsToolDetailsLoggingEnabled"])
    value = os.getenv("DEEPSEEK_ANALYTICS_TOOL_DETAILS")
    return str(value).lower() in {"1", "true", "yes", "on"} if value is not None else True


async def isToolDetailsLoggingEnabled(config: dict[str, Any] | None = None) -> bool:
    return await isAnalyticsToolDetailsLoggingEnabled(config)


async def extractToolInputForTelemetry(tool_name: str, tool_input: dict[str, Any] | None = None) -> dict[str, Any]:
    """Extract low-risk telemetry fields from tool input."""

    tool_input = tool_input or {}
    result: dict[str, Any] = {"tool_name": await sanitizeToolNameForAnalytics(tool_name)}
    for key, value in tool_input.items():
        if key not in _SAFE_KEYS:
            continue
        if key in {"path", "file_path"}:
            result[f"{key}_extension"] = await getFileExtensionForAnalytics(str(value))
        elif key == "command":
            try:
                result["command_name"] = shlex.split(str(value), posix=False)[0]
            except (ValueError, IndexError):
                result["command_name"] = str(value).split(" ", 1)[0] if value else None
            result["command_file_extensions"] = await getFileExtensionsFromBashCommand(str(value))
        else:
            result[key] = str(value)[:200]
    mcp = await extractMcpToolDetails(tool_name)
    if mcp:
        result["mcp"] = mcp
    return result


async def getEventMetadata(
    event_name: str,
    properties: dict[str, Any] | None = None,
    tool_name: str | None = None,
    tool_input: dict[str, Any] | None = None,
) -> dict[str, Any]:
    metadata = {"event": event_name, **(properties or {})}
    if tool_name:
        metadata["tool"] = await extractToolInputForTelemetry(tool_name, tool_input)
    return metadata


async def to1PEventFormat(event_name: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "event_name": await sanitizeToolNameForAnalytics(event_name),
        "event_properties": metadata or {},
        "source": "deepseek_code_python",
    }
