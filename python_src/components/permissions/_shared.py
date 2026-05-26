"""Shared structured permission UI shims."""

from __future__ import annotations

import difflib
from pathlib import Path
from typing import Any


def _pick(mapping: dict[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping[key] is not None:
            return mapping[key]
    return default


def normalize_permission_input(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    if args:
        first = args[0]
        if isinstance(first, dict):
            data.update(first)
        else:
            data["input"] = first
    data.update(kwargs)
    tool_input = data.get("toolInput") or data.get("input") or {}
    if isinstance(tool_input, dict):
        data.update({f"input_{key}": value for key, value in tool_input.items()})
    return data


def permission_title(tool_name: str | None, action: str | None = None) -> str:
    tool = (tool_name or "tool").replace("_", " ")
    if action:
        return f"Allow {tool} to {action}?"
    return f"Allow {tool}?"


def permission_options(kind: str = "default", *, path: str | None = None) -> list[dict[str, Any]]:
    options = [
        {"id": "allow_once", "label": "Allow once", "behavior": "allow", "scope": "once"},
        {"id": "deny", "label": "Deny", "behavior": "deny", "scope": "once"},
    ]
    if kind in {"file", "filesystem", "shell", "powershell"}:
        options.insert(
            1,
            {
                "id": "allow_workspace",
                "label": "Allow in workspace",
                "behavior": "allow",
                "scope": "workspace",
                "path": path,
            },
        )
    return options


def permission_request(
    name: str,
    *args: Any,
    tool_name: str | None = None,
    action: str | None = None,
    kind: str = "default",
    **kwargs: Any,
) -> dict[str, Any]:
    data = normalize_permission_input(*args, **kwargs)
    path = str(_pick(data, "path", "file_path", "input_path", "input_file_path", default="") or "")
    resolved_tool = tool_name or str(_pick(data, "toolName", "tool_name", "tool", default=name))
    return {
        "type": "permission_request",
        "component": name,
        "provider": "deepseek",
        "toolName": resolved_tool,
        "title": permission_title(resolved_tool, action),
        "path": path,
        "input": data,
        "options": permission_options(kind, path=path or None),
    }


def format_permission_explanation(request: dict[str, Any] | None = None, **kwargs: Any) -> str:
    data = dict(request or {})
    data.update(kwargs)
    title = data.get("title") or permission_title(data.get("toolName") or data.get("tool_name"))
    path = data.get("path")
    reason = data.get("reason") or data.get("message") or "DeepSeek Code is requesting permission before taking a local action."
    if path:
        return f"{title}\nTarget: {path}\n{reason}"
    return f"{title}\n{reason}"


def unified_diff(old_text: str, new_text: str, *, fromfile: str = "before", tofile: str = "after") -> str:
    return "\n".join(
        difflib.unified_diff(
            old_text.splitlines(),
            new_text.splitlines(),
            fromfile=fromfile,
            tofile=tofile,
            lineterm="",
        )
    )


def file_write_diff(path: str, content: str, *, cwd: str | None = None) -> dict[str, Any]:
    target = Path(path)
    if not target.is_absolute():
        target = Path(cwd or ".") / target
    target = target.resolve()
    old_text = target.read_text(encoding="utf-8", errors="replace") if target.exists() and target.is_file() else ""
    return {
        "type": "file_diff",
        "provider": "deepseek",
        "path": str(target),
        "exists": target.exists(),
        "diff": unified_diff(old_text, content, fromfile=str(target), tofile=str(target)),
    }


__all__ = [
    "file_write_diff",
    "format_permission_explanation",
    "normalize_permission_input",
    "permission_options",
    "permission_request",
    "permission_title",
    "unified_diff",
]
