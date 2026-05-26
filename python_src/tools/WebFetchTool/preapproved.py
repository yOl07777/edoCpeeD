"""Preapproved host helpers for WebFetchTool."""

from __future__ import annotations

from typing import Any
from urllib.parse import urlparse

PREAPPROVED_HOSTS = {
    "docs.python.org",
    "github.com",
    "raw.githubusercontent.com",
    "api.github.com",
    "developer.mozilla.org",
    "learn.microsoft.com",
    "api-docs.deepseek.com",
}


def _host(value: str) -> str:
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return (parsed.hostname or value).lower().strip(".")


async def isPreapprovedHost(*args: Any, **kwargs: Any) -> bool:
    host = _host(str(args[0] if args else kwargs.get("host") or kwargs.get("url") or ""))
    return host in PREAPPROVED_HOSTS or any(host.endswith(f".{allowed}") for allowed in PREAPPROVED_HOSTS)


__all__ = ["PREAPPROVED_HOSTS", "isPreapprovedHost"]
