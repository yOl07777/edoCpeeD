from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, percent, safe_int, scalar_arg


async def TeleportProgress(*args: Any, **kwargs: Any) -> dict[str, Any]:
    current = safe_int(option(args, kwargs, "current", option(args, kwargs, "completed", scalar_arg(args, 0))))
    total = safe_int(option(args, kwargs, "total", 0))
    status = str(option(args, kwargs, "status", "running" if total and current < total else "ready") or "ready")
    return component_payload("teleport_progress", current=current, total=total, percent=percent(current, total), status=status)


async def teleportWithProgress(*args: Any, **kwargs: Any) -> dict[str, Any]:
    files = list(option(args, kwargs, "files", scalar_arg(args, [])) or [])
    progress = await TeleportProgress(current=len(files), total=len(files), status=option(args, kwargs, "status", "planned"))
    return component_payload("teleport_with_progress", files=files, progress=progress, dryRun=bool(option(args, kwargs, "dryRun", True)))


__all__ = ["TeleportProgress", "teleportWithProgress"]
