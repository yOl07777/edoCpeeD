"""Settings sync schemas for the Python migration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

SYNC_KEYS = {
    "USER_SETTINGS": "~/.deepseek/settings.json",
    "USER_MEMORY": "~/.deepseek/DEEPSEEK.md",
    "projectSettings": lambda projectId: f"projects/{projectId}/.deepseek/settings.local.json",
    "projectMemory": lambda projectId: f"projects/{projectId}/DEEPSEEK.local.md",
}


@dataclass
class SchemaIssue:
    path: list[str]
    message: str


@dataclass
class SchemaError:
    issues: list[SchemaIssue]


@dataclass
class SchemaResult:
    success: bool
    data: Any = None
    error: SchemaError | None = None


class _Schema:
    def __init__(self, parser: Callable[[Any], Any]) -> None:
        self._parser = parser

    def parse(self, value: Any) -> Any:
        return self._parser(value)

    def safeParse(self, value: Any) -> SchemaResult:
        try:
            return SchemaResult(True, self.parse(value), None)
        except ValueError as exc:
            return SchemaResult(False, None, SchemaError([SchemaIssue([], str(exc))]))


def _content(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or not isinstance(value.get("entries", {}), dict):
        raise ValueError("sync content must contain entries object")
    return {"entries": {str(k): str(v) for k, v in value.get("entries", {}).items()}}


def _data(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("sync data must be an object")
    return {
        "userId": str(value.get("userId") or "local"),
        "version": int(value.get("version") or 1),
        "lastModified": str(value.get("lastModified") or ""),
        "checksum": str(value.get("checksum") or ""),
        "content": _content(value.get("content", {})),
    }


def UserSyncContentSchema() -> _Schema:
    return _Schema(_content)


def UserSyncDataSchema() -> _Schema:
    return _Schema(_data)


SettingsSyncFetchResult = dict[str, Any]
SettingsSyncUploadResult = dict[str, Any]
UserSyncData = dict[str, Any]


__all__ = [
    "SYNC_KEYS",
    "SettingsSyncFetchResult",
    "SettingsSyncUploadResult",
    "UserSyncContentSchema",
    "UserSyncData",
    "UserSyncDataSchema",
]
