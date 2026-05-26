"""Local team memory sync service for the Python migration."""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .secretScanner import scanForSecrets

MAX_PUT_BODY_BYTES = 200_000


@dataclass
class SyncState:
    lastKnownChecksum: str | None = None
    serverChecksums: dict[str, str] = field(default_factory=dict)
    serverMaxEntries: int | None = None


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser().resolve() if root else (Path.home() / ".deepcode").resolve()


def _team_dir() -> Path:
    return Path(os.getenv("DEEPCODE_TEAM_MEMORY_DIR") or (_config_home() / "team-memory")).resolve()


def _remote_path() -> Path:
    return _config_home() / "team-memory-sync.json"


async def createSyncState(*args: Any, **kwargs: Any) -> SyncState:
    return SyncState()


async def hashContent(*args: Any, **kwargs: Any) -> str:
    content = str(kwargs.get("content") if "content" in kwargs else (args[0] if args else ""))
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


async def isTeamMemorySyncAvailable(*args: Any, **kwargs: Any) -> bool:
    value = os.getenv("DEEPCODE_TEAM_MEMORY_SYNC") or os.getenv("DEEPSEEK_TEAM_MEMORY_SYNC")
    return True if value is None else value.lower() in {"1", "true", "yes", "on"}


def _safe_key(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    if rel.startswith("../") or rel == ".." or "/../" in rel:
        raise ValueError("Invalid team memory path")
    return rel


async def _read_local_entries() -> dict[str, str]:
    root = _team_dir()
    if not root.exists():
        return {}
    entries: dict[str, str] = {}
    for path in root.rglob("*"):
        if path.is_file():
            try:
                entries[_safe_key(path, root)] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
    return entries


def _read_remote() -> dict[str, Any]:
    try:
        data = json.loads(_remote_path().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _write_remote(entries: dict[str, str], state: SyncState | None = None) -> dict[str, Any]:
    checksums = {key: "sha256:" + hashlib.sha256(value.encode("utf-8")).hexdigest() for key, value in entries.items()}
    checksum = "sha256:" + hashlib.sha256(json.dumps(checksums, sort_keys=True).encode("utf-8")).hexdigest()
    data = {
        "organizationId": "local",
        "repo": "local",
        "version": int((_read_remote().get("version") or 0)) + 1,
        "lastModified": datetime.now(timezone.utc).isoformat(),
        "checksum": checksum,
        "content": {"entries": entries, "entryChecksums": checksums},
    }
    path = _remote_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    if state is not None:
        state.lastKnownChecksum = checksum
        state.serverChecksums = dict(checksums)
    return data


async def batchDeltaByBytes(*args: Any, **kwargs: Any) -> list[dict[str, str]]:
    entries = kwargs.get("entries") if "entries" in kwargs else (args[0] if args else {})
    max_bytes = int(kwargs.get("maxBytes") or (args[1] if len(args) > 1 else MAX_PUT_BODY_BYTES))
    batches: list[dict[str, str]] = []
    current: dict[str, str] = {}
    current_size = 0
    for key, value in dict(entries or {}).items():
        item_size = len(str(key).encode("utf-8")) + len(str(value).encode("utf-8"))
        if current and current_size + item_size > max_bytes:
            batches.append(current)
            current = {}
            current_size = 0
        current[str(key)] = str(value)
        current_size += item_size
    if current:
        batches.append(current)
    return batches


async def pullTeamMemory(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = kwargs.get("state") or (args[0] if args else None)
    data = _read_remote()
    entries = ((data.get("content") or {}).get("entries") or {}) if data else {}
    if not entries:
        return {"success": True, "isEmpty": True, "filesWritten": 0}
    root = _team_dir()
    written = 0
    for key, value in entries.items():
        target = (root / str(key)).resolve()
        if root not in target.parents and target != root:
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(str(value), encoding="utf-8")
        written += 1
    if isinstance(state, SyncState):
        state.lastKnownChecksum = data.get("checksum")
        state.serverChecksums = dict((data.get("content") or {}).get("entryChecksums") or {})
    return {"success": True, "filesWritten": written, "checksum": data.get("checksum")}


async def pushTeamMemory(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = kwargs.get("state") or (args[0] if args else None)
    if not await isTeamMemorySyncAvailable():
        return {"success": False, "filesUploaded": 0, "error": "Team memory sync disabled", "errorType": "no_oauth"}
    entries = await _read_local_entries()
    skipped: list[dict[str, str]] = []
    clean: dict[str, str] = {}
    for key, value in entries.items():
        matches = await scanForSecrets(value)
        if matches:
            skipped.append({"path": key, **matches[0]})
        else:
            clean[key] = value
    remote = _read_remote()
    existing = dict(((remote.get("content") or {}).get("entries") or {}))
    merged = {**existing, **clean}
    data = _write_remote(merged, state if isinstance(state, SyncState) else None)
    return {"success": True, "filesUploaded": len(clean), "checksum": data["checksum"], "skippedSecrets": skipped}


async def syncTeamMemory(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = kwargs.get("state") or (args[0] if args else await createSyncState())
    pull = await pullTeamMemory(state)
    push = await pushTeamMemory(state)
    return {"success": bool(pull.get("success") and push.get("success")), "pull": pull, "push": push}


__all__ = [
    "SyncState",
    "batchDeltaByBytes",
    "createSyncState",
    "hashContent",
    "isTeamMemorySyncAvailable",
    "pullTeamMemory",
    "pushTeamMemory",
    "syncTeamMemory",
]
