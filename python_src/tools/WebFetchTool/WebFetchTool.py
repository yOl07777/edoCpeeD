from __future__ import annotations

import re
from typing import Any
from urllib.parse import urlparse

import httpx

from python_src.tools.base import PythonTool, object_schema


def _html_to_text(html: str) -> str:
    html = re.sub(r"(?is)<(script|style).*?>.*?</\1>", "", html)
    html = re.sub(r"(?s)<[^>]+>", " ", html)
    html = re.sub(r"\s+", " ", html)
    return html.strip()


async def web_fetch(
    url: str,
    *,
    max_chars: int = 20_000,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DeepSeek-Code/0.1; +https://api-docs.deepseek.com)",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,text/plain;q=0.8,*/*;q=0.5",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7",
    }
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        response = error.response
        host = urlparse(str(response.url or url)).netloc
        blocked = response.status_code in {401, 403, 451}
        return {
            "url": str(response.url or url),
            "status_code": response.status_code,
            "ok": False,
            "error": f"HTTP {response.status_code} while fetching {host}",
            "blocked": blocked,
            "content": "",
            "truncated": False,
            "suggestion": "该站点拒绝了自动抓取。请改用 web_search 查找其他来源，或让用户提供可访问的页面内容。",
        }
    except httpx.RequestError as error:
        return {
            "url": url,
            "status_code": None,
            "ok": False,
            "error": str(error),
            "blocked": False,
            "content": "",
            "truncated": False,
            "suggestion": "网络请求失败。请改用 web_search 查找其他来源，或稍后重试。",
        }
    content_type = response.headers.get("content-type", "")
    text = response.text
    if "html" in content_type:
        text = _html_to_text(text)
    return {
        "url": str(response.url),
        "status_code": response.status_code,
        "ok": True,
        "content_type": content_type,
        "content": text[:max_chars],
        "truncated": len(text) > max_chars,
    }


WebFetchTool = PythonTool(
    name="web_fetch",
    description="Fetch a URL and return readable text content.",
    parameters=object_schema(
        {
            "url": {"type": "string", "description": "URL to fetch."},
            "max_chars": {"type": "integer", "description": "Maximum returned characters.", "default": 20000},
        },
        required=["url"],
    ),
    handler=web_fetch,
    read_only=True,
)
