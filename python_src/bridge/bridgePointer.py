"""Crash-recovery pointer storage for bridge sessions."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

BRIDGE_POINTER_TTL_MS = 4 * 60 * 60 * 1000
MAX_WORKTREE_FANOUT = 50


def _projects_dir() -> Path:
    root = os.getenv("DEEPCODE_PROJECTS_DIR") or os.getenv("XDG_STATE_HOME")
    if root:
        return Path(root).expanduser() / "deepcode" / "projects"
    return Path.home() / ".deepcode" / "projects"


def _sanitize_path(path: str) -> str:
    resolved = str(Path(path).expanduser().resolve())
    drive = resolved.replace(":", "")
    return "".join(ch if ch.isalnum() or ch in "._-" else "-" for ch in drive).strip("-")


def getBridgePointerPath(dir: str) -> str:
    return str(_projects_dir() / _sanitize_path(dir) / "bridge-pointer.json")


async def writeBridgePointer(dir: str, pointer: dict[str, Any]) -> None:
    path = Path(getBridgePointerPath(dir))
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(pointer, ensure_ascii=False), encoding="utf-8")
    except OSError:
        return


def _validate_pointer(data: Any) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    if not isinstance(data.get("sessionId"), str):
        return None
    if not isinstance(data.get("environmentId"), str):
        return None
    if data.get("source") not in {"standalone", "repl"}:
        return None
    return {
        "sessionId": data["sessionId"],
        "environmentId": data["environmentId"],
        "source": data["source"],
    }


async def readBridgePointer(dir: str) -> dict[str, Any] | None:
    path = Path(getBridgePointerPath(dir))
    try:
        stat = path.stat()
        raw = path.read_text(encoding="utf-8")
        parsed = json.loads(raw)
    except (OSError, ValueError):
        return None
    pointer = _validate_pointer(parsed)
    if pointer is None:
        await clearBridgePointer(dir)
        return None
    age_ms = max(0, int(time.time() * 1000 - stat.st_mtime * 1000))
    if age_ms > BRIDGE_POINTER_TTL_MS:
        await clearBridgePointer(dir)
        return None
    pointer["ageMs"] = age_ms
    return pointer


async def readBridgePointerAcrossWorktrees(dir: str) -> dict[str, Any] | None:
    here = await readBridgePointer(dir)
    if here:
        return {"pointer": here, "dir": dir}
    candidates = [p for p in Path(dir).parent.iterdir() if p.is_dir()][:MAX_WORKTREE_FANOUT]
    freshest: dict[str, Any] | None = None
    for candidate in candidates:
        pointer = await readBridgePointer(str(candidate))
        if pointer and (freshest is None or pointer["ageMs"] < freshest["pointer"]["ageMs"]):
            freshest = {"pointer": pointer, "dir": str(candidate)}
    return freshest


async def clearBridgePointer(dir: str) -> None:
    try:
        Path(getBridgePointerPath(dir)).unlink()
    except FileNotFoundError:
        return
    except OSError:
        return
