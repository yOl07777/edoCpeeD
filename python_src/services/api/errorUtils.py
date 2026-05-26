"""Formatting and sanitization helpers for API errors."""

from __future__ import annotations

import re
from typing import Any

from .errors import API_ERROR_MESSAGE_PREFIX, classifyAPIError

_SECRET_RE = re.compile(r"(sk-[A-Za-z0-9_\-]{8,}|Bearer\s+[A-Za-z0-9._\-]+|api[_-]?key[=:]\s*[^,\s]+)", re.I)


async def sanitizeAPIError(error: Any) -> str:
    text = str(error if not isinstance(error, dict) else error.get("message", error))
    return _SECRET_RE.sub("[redacted]", text)


async def getSSLErrorHint(error: Any) -> str | None:
    text = str(error).lower()
    if "ssl" in text or "certificate" in text or "tls" in text:
        return "Check the DeepSeek endpoint URL, proxy certificate, or system trust store."
    return None


async def extractConnectionErrorDetails(error: Any) -> dict[str, Any]:
    text = await sanitizeAPIError(error)
    lowered = text.lower()
    return {
        "message": text,
        "ssl": "ssl" in lowered or "certificate" in lowered or "tls" in lowered,
        "timeout": "timeout" in lowered or "timed out" in lowered,
        "dns": "enotfound" in lowered or "name resolution" in lowered or "getaddrinfo" in lowered,
    }


async def formatAPIError(error: Any) -> str:
    classified = await classifyAPIError(error)
    message = await sanitizeAPIError(classified["message"])
    prefix = API_ERROR_MESSAGE_PREFIX
    status = f" status={classified['status']}" if classified.get("status") else ""
    hint = await getSSLErrorHint(error)
    formatted = f"{prefix}{status} {message}".strip()
    return f"{formatted}\n{hint}" if hint else formatted

