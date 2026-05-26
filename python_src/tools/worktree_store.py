from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class WorktreeState:
    active: bool = False
    path: str = ""
    branch: str = ""
    reason: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"active": self.active, "path": self.path, "branch": self.branch, "reason": self.reason}


WORKTREE_STATE = WorktreeState()


def enter_worktree(path: str | None = None, *, branch: str = "", reason: str = "", cwd: str | None = None) -> WorktreeState:
    root = Path(cwd or os.getcwd()).resolve()
    target = Path(path or root).expanduser()
    if not target.is_absolute():
        target = root / target
    WORKTREE_STATE.active = True
    WORKTREE_STATE.path = str(target.resolve(strict=False))
    WORKTREE_STATE.branch = branch
    WORKTREE_STATE.reason = reason
    return WORKTREE_STATE


def exit_worktree() -> WorktreeState:
    WORKTREE_STATE.active = False
    return WORKTREE_STATE


def reset_worktree() -> None:
    WORKTREE_STATE.active = False
    WORKTREE_STATE.path = ""
    WORKTREE_STATE.branch = ""
    WORKTREE_STATE.reason = ""


__all__ = ["WORKTREE_STATE", "WorktreeState", "enter_worktree", "exit_worktree", "reset_worktree"]
