"""Policy limits schemas for the Python migration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

PolicyLimitsResponse = dict[str, dict[str, dict[str, bool]]]
PolicyLimitsFetchResult = dict[str, Any]


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


class _PolicyLimitsResponseSchema:
    def parse(self, value: Any) -> dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("Policy limits response must be an object")
        restrictions = value.get("restrictions", {})
        if restrictions is None:
            restrictions = {}
        if not isinstance(restrictions, dict):
            raise ValueError("restrictions must be an object")
        normalized: dict[str, dict[str, bool]] = {}
        for key, item in restrictions.items():
            if not isinstance(item, dict) or "allowed" not in item:
                raise ValueError(f"restriction {key} must include allowed")
            normalized[str(key)] = {"allowed": bool(item["allowed"])}
        return {"restrictions": normalized}

    def safeParse(self, value: Any) -> SchemaResult:
        try:
            return SchemaResult(True, self.parse(value), None)
        except ValueError as exc:
            return SchemaResult(False, None, SchemaError([SchemaIssue([], str(exc))]))


def PolicyLimitsResponseSchema() -> _PolicyLimitsResponseSchema:
    return _PolicyLimitsResponseSchema()


__all__ = [
    "PolicyLimitsFetchResult",
    "PolicyLimitsResponse",
    "PolicyLimitsResponseSchema",
    "SchemaError",
    "SchemaIssue",
    "SchemaResult",
]
