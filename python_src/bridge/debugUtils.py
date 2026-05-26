"""Debug formatting helpers for bridge and remote-control flows."""

from __future__ import annotations

import json
import re
from typing import Any

DEBUG_MSG_LIMIT = 2000
SECRET_FIELD_NAMES = ("token", "secret", "authorization", "api_key", "apikey", "password")
REDACT_MIN_LENGTH = 16
SECRET_PATTERN = re.compile(
    r"(?P<prefix>(?:token|secret|authorization|api[_-]?key|password)[\"']?\s*[:=]\s*[\"']?)"
    r"(?P<value>[A-Za-z0-9_\-./+=]{16,})",
    re.IGNORECASE,
)


def redactSecrets(s: str) -> str:
    def repl(match: re.Match[str]) -> str:
        value = match.group("value")
        redacted = f"{value[:8]}...{value[-4:]}" if len(value) >= REDACT_MIN_LENGTH else "***"
        return match.group("prefix") + redacted

    return SECRET_PATTERN.sub(repl, s)


def debugTruncate(s: str) -> str:
    flat = s.replace("\n", "\\n")
    if len(flat) <= DEBUG_MSG_LIMIT:
        return flat
    return flat[:DEBUG_MSG_LIMIT] + f"... <truncated {len(flat) - DEBUG_MSG_LIMIT} chars>"


def _redact_object(value: Any) -> Any:
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            if any(name in str(key).lower() for name in SECRET_FIELD_NAMES):
                result[key] = "***"
            else:
                result[key] = _redact_object(item)
        return result
    if isinstance(value, list):
        return [_redact_object(item) for item in value]
    return value


def debugBody(data: Any) -> str:
    if isinstance(data, str):
        raw = data
    else:
        try:
            raw = json.dumps(_redact_object(data), ensure_ascii=False, default=str)
        except TypeError:
            raw = str(data)
    return debugTruncate(redactSecrets(raw))


def extractErrorDetail(data: Any) -> str | None:
    if isinstance(data, str):
        return data
    if not isinstance(data, dict):
        return None
    for key in ("detail", "message", "error", "error_description"):
        value = data.get(key)
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            nested = extractErrorDetail(value)
            if nested:
                return nested
    return None


def extractHttpStatus(err: Any) -> int | None:
    for attr in ("status_code", "status"):
        value = getattr(err, attr, None)
        if isinstance(value, int):
            return value
    response = getattr(err, "response", None)
    if response is not None:
        return extractHttpStatus(response)
    if isinstance(err, dict):
        for key in ("status_code", "status"):
            value = err.get(key)
            if isinstance(value, int):
                return value
        if "response" in err:
            return extractHttpStatus(err["response"])
    return None


def describeAxiosError(err: Any) -> str:
    message = str(err)
    response = getattr(err, "response", None)
    if isinstance(err, dict):
        response = err.get("response", response)
        message = str(err.get("message") or message)
    status = extractHttpStatus(response or err)
    data = getattr(response, "data", None)
    if data is None and hasattr(response, "json"):
        try:
            data = response.json()
        except Exception:
            data = None
    if isinstance(response, dict):
        data = response.get("data", data)
    detail = extractErrorDetail(data)
    prefix = f"HTTP {status}: " if status is not None else ""
    return prefix + (detail or message)


def logBridgeSkip(reason: str, **details: Any) -> str:
    suffix = f" {debugBody(details)}" if details else ""
    return f"[bridge] skipped: {reason}{suffix}"
