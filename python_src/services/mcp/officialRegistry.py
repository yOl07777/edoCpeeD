"""Offline official MCP registry shim.

The original implementation prefetches Anthropic's registry.  This migration
keeps lookups fail-closed by default and lets tests or local callers seed URLs
explicitly through arguments or environment JSON.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.parse import urlparse, urlunparse

_official_urls: set[str] | None = None


def _normalize_url(url: str) -> str | None:
    try:
        parsed = urlparse(str(url))
        if not parsed.scheme or not parsed.netloc:
            return None
        normalized = parsed._replace(query="", fragment="", path=parsed.path.rstrip("/"))
        return urlunparse(normalized)
    except Exception:
        return None


def _extract_urls(value: Any) -> set[str]:
    urls: set[str] = set()
    if isinstance(value, str):
        normalized = _normalize_url(value)
        if normalized:
            urls.add(normalized)
    elif isinstance(value, dict):
        for key in ("url", "serverUrl"):
            if key in value:
                urls.update(_extract_urls(value[key]))
        if isinstance(value.get("servers"), (list, tuple)):
            urls.update(_extract_urls(value["servers"]))
        for remote in value.get("remotes", []) or []:
            urls.update(_extract_urls(remote))
        if isinstance(value.get("server"), dict):
            urls.update(_extract_urls(value["server"]))
    elif isinstance(value, (list, tuple, set)):
        for item in value:
            urls.update(_extract_urls(item))
    return urls


async def isOfficialMcpUrl(*args: Any, **kwargs: Any) -> bool:
    url = str(kwargs.get("url") or (args[0] if args else ""))
    normalized = _normalize_url(url)
    return bool(normalized and _official_urls and normalized in _official_urls)


async def prefetchOfficialMcpUrls(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _official_urls
    source = kwargs.get("registry") or kwargs.get("urls") or (args[0] if args else None)
    if source is None:
        raw = os.getenv("DEEPCODE_OFFICIAL_MCP_URLS") or os.getenv("DEEPSEEK_OFFICIAL_MCP_URLS")
        if raw:
            try:
                source = json.loads(raw)
            except Exception:
                source = [part.strip() for part in raw.split(",") if part.strip()]
    _official_urls = _extract_urls(source) if source is not None else set()
    return {"count": len(_official_urls), "urls": sorted(_official_urls)}


async def resetOfficialMcpUrlsForTesting(*args: Any, **kwargs: Any) -> None:
    global _official_urls
    _official_urls = None


__all__ = ["isOfficialMcpUrl", "prefetchOfficialMcpUrls", "resetOfficialMcpUrlsForTesting"]
