"""Implementation helpers for the DeepSeek IDE command."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable


def formatWorkspaceFolders(workspaceFolders: list[str] | tuple[str, ...] | None = None) -> str:
    folders = [str(folder) for folder in (workspaceFolders or [])]
    if not folders:
        return "No workspace folders"
    if len(folders) <= 2:
        return ", ".join(folders)
    return ", ".join(folders[:2]) + f", +{len(folders) - 2} more"


def _detect_workspace(cwd: str | None = None) -> dict[str, Any]:
    root = Path(cwd or Path.cwd()).resolve()
    markers = {
        "vscode": root / ".vscode",
        "cursor": root / ".cursor",
        "windsurf": root / ".windsurf",
        "jetbrains": root / ".idea",
    }
    detected = [
        {"name": name, "path": str(path), "present": path.exists()}
        for name, path in markers.items()
        if path.exists()
    ]
    return {"cwd": str(root), "detected": detected, "workspaceFolders": [str(root)]}


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    cwd = context.get("cwd") if isinstance(context, dict) else None
    status = _detect_workspace(cwd)
    action = args.strip().lower() if args else "status"
    if action == "open":
        value = (
            "IDE opening is not performed by the Python migration shim. "
            f"Open this workspace manually: {status['cwd']}"
        )
    elif status["detected"]:
        names = ", ".join(item["name"] for item in status["detected"])
        value = f"Detected local IDE configuration: {names}."
    else:
        value = "No local IDE configuration directories detected for this workspace."
    if onDone:
        onDone(value)
    return {"type": "ide", "value": value, "action": action, "status": status}
