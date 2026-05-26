"""Remote managed settings schemas for the Python migration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

RemoteManagedSettingsResponse = dict[str, Any]
RemoteManagedSettingsFetchResult = dict[str, Any]


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


class _RemoteManagedSettingsResponseSchema:
    def parse(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("Remote managed settings response must be an object")
        uuid = str(value.get("uuid") or "local")
        checksum = str(value.get("checksum") or "")
        settings = value.get("settings", {})
        if settings is None:
            settings = {}
        if not isinstance(settings, dict):
            raise ValueError("settings must be an object")
        return {"uuid": uuid, "checksum": checksum, "settings": dict(settings)}

    def safeParse(self, value: Any) -> SchemaResult:
        try:
            return SchemaResult(True, self.parse(value), None)
        except ValueError as exc:
            return SchemaResult(False, None, SchemaError([SchemaIssue([], str(exc))]))


def RemoteManagedSettingsResponseSchema() -> _RemoteManagedSettingsResponseSchema:
    return _RemoteManagedSettingsResponseSchema()


__all__ = [
    "RemoteManagedSettingsFetchResult",
    "RemoteManagedSettingsResponse",
    "RemoteManagedSettingsResponseSchema",
    "SchemaError",
    "SchemaIssue",
    "SchemaResult",
]
