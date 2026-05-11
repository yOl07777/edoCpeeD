from __future__ import annotations

from pathlib import Path


def resolve_workspace_path(path: str, *, cwd: str | None = None) -> Path:
    base = Path(cwd or ".").resolve()
    target = Path(path)
    if not target.is_absolute():
        target = base / target
    target = target.resolve()
    try:
        target.relative_to(base)
    except ValueError as exc:
        raise PermissionError(f"Path escapes workspace: {target}") from exc
    return target
