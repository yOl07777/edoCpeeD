from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def WorktreeExitDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    dirty_files = normalize_items(option(args, kwargs, "dirtyFiles", option(args, kwargs, "files", scalar_arg(args, []))), text_key="path")
    confirmed = bool(option(args, kwargs, "confirmed", False))
    return component_payload(
        "worktree_exit_dialog",
        dirtyFiles=dirty_files,
        dirtyCount=len(dirty_files),
        confirmed=confirmed,
        canExit=confirmed or not dirty_files,
    )


__all__ = ["WorktreeExitDialog"]
