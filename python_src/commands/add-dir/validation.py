"""Validation helpers for `/add-dir`."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _working_dirs(permissionContext: dict[str, Any] | None = None) -> list[Path]:
    ctx = permissionContext or {}
    raw_dirs = (
        ctx.get("workingDirectories")
        or ctx.get("working_dirs")
        or ctx.get("directories")
        or ctx.get("additionalDirectories")
        or []
    )
    dirs = raw_dirs.values() if isinstance(raw_dirs, dict) else raw_dirs
    result: list[Path] = []
    for item in dirs:
        path = item.get("path") if isinstance(item, dict) else item
        if path:
            result.append(Path(str(path)).expanduser().resolve())
    return result


def _in_working_path(path: Path, working_dir: Path) -> bool:
    try:
        path.relative_to(working_dir)
        return True
    except ValueError:
        return False


async def validateDirectoryForWorkspace(directoryPath: str, permissionContext: dict[str, Any] | None = None) -> dict[str, Any]:
    if not directoryPath:
        return {"resultType": "emptyPath"}
    absolute = Path(directoryPath).expanduser().resolve()
    if not absolute.exists():
        return {"resultType": "pathNotFound", "directoryPath": directoryPath, "absolutePath": str(absolute)}
    if not absolute.is_dir():
        return {"resultType": "notADirectory", "directoryPath": directoryPath, "absolutePath": str(absolute)}
    for working_dir in _working_dirs(permissionContext):
        if _in_working_path(absolute, working_dir):
            return {"resultType": "alreadyInWorkingDirectory", "directoryPath": directoryPath, "workingDir": str(working_dir)}
    return {"resultType": "success", "absolutePath": str(absolute)}


def addDirHelpMessage(result: dict[str, Any]) -> str:
    result_type = result.get("resultType")
    if result_type == "emptyPath":
        return "Please provide a directory path."
    if result_type == "pathNotFound":
        return f"Path {result.get('absolutePath')} was not found."
    if result_type == "notADirectory":
        parent = str(Path(str(result.get("absolutePath"))).parent)
        return f"{result.get('directoryPath')} is not a directory. Did you mean to add the parent directory {parent}?"
    if result_type == "alreadyInWorkingDirectory":
        return f"{result.get('directoryPath')} is already accessible within the existing working directory {result.get('workingDir')}."
    if result_type == "success":
        return f"Added {result.get('absolutePath')} as a working directory."
    return "Could not add working directory."
