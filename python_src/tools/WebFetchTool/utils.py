"""WebFetchTool utility helpers."""

from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

from python_src.tools.WebFetchTool.preapproved import isPreapprovedHost
from python_src.tools.WebFetchTool.WebFetchTool import web_fetch

MAX_MARKDOWN_LENGTH = 20_000
BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0", "::1"}

_CACHE: dict[str, dict[str, Any]] = {}


def _payload(args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    if args and isinstance(args[0], dict):
        return {**args[0], **kwargs}
    return dict(kwargs)


async def validateURL(*args: Any, **kwargs: Any) -> dict[str, Any]:
    url = str(args[0] if args else kwargs.get("url", ""))
    parsed = urlparse(url)
    ok = parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    reason = None if ok else "URL must use http or https and include a host"
    if ok and (parsed.hostname or "").lower() in BLOCKED_HOSTS:
        ok = False
        reason = "Local/private loopback hosts are blocked"
    return {"ok": ok, "url": url, "scheme": parsed.scheme, "host": parsed.hostname, "reason": reason}


async def checkDomainBlocklist(*args: Any, **kwargs: Any) -> dict[str, Any]:
    url = str(args[0] if args else kwargs.get("url", ""))
    host = (urlparse(url).hostname or "").lower()
    blocked = host in BLOCKED_HOSTS
    return {"blocked": blocked, "host": host, "reason": "blocked local host" if blocked else None}


async def isPreapprovedUrl(*args: Any, **kwargs: Any) -> bool:
    url = str(args[0] if args else kwargs.get("url", ""))
    return await isPreapprovedHost(url=url)


async def isPermittedRedirect(*args: Any, **kwargs: Any) -> bool:
    data = _payload(args, kwargs)
    source = urlparse(str(data.get("from_url") or data.get("fromUrl") or data.get("source") or ""))
    target = urlparse(str(data.get("to_url") or data.get("toUrl") or data.get("target") or ""))
    if target.scheme not in {"http", "https"} or not target.hostname:
        return False
    if (target.hostname or "").lower() in BLOCKED_HOSTS:
        return False
    return source.hostname == target.hostname or await isPreapprovedHost(host=target.hostname)


async def getWithPermittedRedirects(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    url = str(data.get("url") or (args[0] if args else ""))
    validation = await validateURL(url)
    if not validation["ok"]:
        return {"ok": False, "url": url, "error": validation["reason"], "content": "", "truncated": False}
    result = await web_fetch(url, max_chars=int(data.get("max_chars") or data.get("maxChars") or MAX_MARKDOWN_LENGTH))
    _CACHE[url] = result
    return result


async def getURLMarkdownContent(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    url = str(data.get("url") or (args[0] if args else ""))
    if url in _CACHE:
        return _CACHE[url]
    return await getWithPermittedRedirects(url=url, **{key: value for key, value in data.items() if key != "url"})


async def applyPromptToMarkdown(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = _payload(args, kwargs)
    markdown = str(data.get("markdown") or data.get("content") or (args[0] if args else ""))
    prompt = str(data.get("prompt") or data.get("question") or "")
    max_length = int(data.get("max_length") or data.get("maxLength") or MAX_MARKDOWN_LENGTH)
    normalized = re.sub(r"\n{3,}", "\n\n", markdown).strip()
    return {
        "prompt": prompt,
        "markdown": normalized[:max_length],
        "truncated": len(normalized) > max_length,
    }


async def clearWebFetchCache(*args: Any, **kwargs: Any) -> dict[str, Any]:
    count = len(_CACHE)
    _CACHE.clear()
    return {"cleared": count}


__all__ = [
    "MAX_MARKDOWN_LENGTH",
    "applyPromptToMarkdown",
    "checkDomainBlocklist",
    "clearWebFetchCache",
    "getURLMarkdownContent",
    "getWithPermittedRedirects",
    "isPermittedRedirect",
    "isPreapprovedUrl",
    "validateURL",
]
