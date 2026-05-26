"""Local settings sync service for the Python migration."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .types import SYNC_KEYS, UserSyncDataSchema

_download_result: bool | None = None


def _config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser().resolve() if root else (Path.home() / ".deepcode").resolve()


def _cwd() -> Path:
    return Path(os.getenv("DEEPCODE_CWD") or os.getcwd()).resolve()


def _store_path() -> Path:
    return _config_home() / "settings-sync.json"


def _settings_path() -> Path:
    return _config_home() / "settings.json"


def _memory_path() -> Path:
    return _config_home() / "DEEPSEEK.md"


def _project_id() -> str:
    return hashlib.sha1(str(_cwd()).encode("utf-8")).hexdigest()[:16]


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _checksum(entries: dict[str, str]) -> str:
    raw = json.dumps(entries, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.md5(raw).hexdigest()


def _store_from_entries(entries: dict[str, str]) -> dict[str, Any]:
    return {
        "userId": "local",
        "version": 1,
        "lastModified": datetime.now(timezone.utc).isoformat(),
        "checksum": _checksum(entries),
        "content": {"entries": entries},
    }


def _load_store() -> dict[str, Any] | None:
    raw = os.getenv("DEEPCODE_SETTINGS_SYNC") or os.getenv("DEEPSEEK_SETTINGS_SYNC")
    if raw:
        try:
            parsed = json.loads(raw)
            return parsed if isinstance(parsed, dict) and "content" in parsed else _store_from_entries(parsed if isinstance(parsed, dict) else {})
        except Exception:
            return None
    data = _read_json(_store_path())
    return data


def _local_entries() -> dict[str, str]:
    entries: dict[str, str] = {}
    if _settings_path().exists():
        entries[str(SYNC_KEYS["USER_SETTINGS"])] = _settings_path().read_text(encoding="utf-8")
    if _memory_path().exists():
        entries[str(SYNC_KEYS["USER_MEMORY"])] = _memory_path().read_text(encoding="utf-8")
    project_key = SYNC_KEYS["projectSettings"](_project_id())
    local_project = _cwd() / ".deepseek_project.json"
    if local_project.exists():
        entries[project_key] = local_project.read_text(encoding="utf-8")
    return entries


def _apply_entries(entries: dict[str, str]) -> int:
    count = 0
    for key, value in entries.items():
        if key == SYNC_KEYS["USER_SETTINGS"]:
            _write_text(_settings_path(), value)
        elif key == SYNC_KEYS["USER_MEMORY"]:
            _write_text(_memory_path(), value)
        elif key.startswith("projects/") and key.endswith("/.deepseek/settings.local.json"):
            _write_text(_cwd() / ".deepseek_project.json", value)
        else:
            continue
        count += 1
    return count


async def _resetDownloadPromiseForTesting(*args: Any, **kwargs: Any) -> None:
    global _download_result
    _download_result = None


async def downloadUserSettings(*args: Any, **kwargs: Any) -> bool:
    global _download_result
    if _download_result is not None:
        return _download_result
    _download_result = await redownloadUserSettings()
    return _download_result


async def redownloadUserSettings(*args: Any, **kwargs: Any) -> bool:
    store = _load_store()
    parsed = UserSyncDataSchema().safeParse(store)
    if not parsed.success:
        return False
    entries = parsed.data["content"]["entries"]
    return _apply_entries(entries) > 0


async def uploadUserSettingsInBackground(*args: Any, **kwargs: Any) -> dict[str, Any]:
    entries = _local_entries()
    store = _store_from_entries(entries)
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"success": True, "entries": len(entries), "checksum": store["checksum"], "path": str(path)}


__all__ = [
    "_resetDownloadPromiseForTesting",
    "downloadUserSettings",
    "redownloadUserSettings",
    "uploadUserSettingsInBackground",
]
