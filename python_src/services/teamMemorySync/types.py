"""Team memory sync schemas for the Python migration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


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
        raise ValueError("team memory content must contain entries object")
    entries = {str(k): str(v) for k, v in value.get("entries", {}).items()}
    checksums = {str(k): str(v) for k, v in (value.get("entryChecksums") or {}).items()}
    return {"entries": entries, "entryChecksums": checksums}


def _data(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError("team memory data must be an object")
    return {
        "organizationId": str(value.get("organizationId") or "local"),
        "repo": str(value.get("repo") or "local"),
        "version": int(value.get("version") or 1),
        "lastModified": str(value.get("lastModified") or ""),
        "checksum": str(value.get("checksum") or ""),
        "content": _content(value.get("content", {})),
    }


def _too_many(value: Any) -> dict[str, Any]:
    details = (((value or {}).get("error") or {}).get("details") or {}) if isinstance(value, dict) else {}
    if details.get("error_code") != "team_memory_too_many_entries":
        raise ValueError("not a team_memory_too_many_entries error")
    return {"error": {"details": {"error_code": "team_memory_too_many_entries", "max_entries": int(details["max_entries"]), "received_entries": int(details["received_entries"])}}}


def TeamMemoryContentSchema() -> _Schema:
    return _Schema(_content)


def TeamMemoryDataSchema() -> _Schema:
    return _Schema(_data)


def TeamMemoryTooManyEntriesSchema() -> _Schema:
    return _Schema(_too_many)


SkippedSecretFile = dict[str, str]
TeamMemoryData = dict[str, Any]
TeamMemoryHashesResult = dict[str, Any]
TeamMemorySyncFetchResult = dict[str, Any]
TeamMemorySyncPushResult = dict[str, Any]
TeamMemorySyncUploadResult = dict[str, Any]


__all__ = [
    "SkippedSecretFile",
    "TeamMemoryContentSchema",
    "TeamMemoryData",
    "TeamMemoryDataSchema",
    "TeamMemoryHashesResult",
    "TeamMemorySyncFetchResult",
    "TeamMemorySyncPushResult",
    "TeamMemorySyncUploadResult",
    "TeamMemoryTooManyEntriesSchema",
]
