from __future__ import annotations

import re
from html import unescape
from typing import Any
from urllib.parse import quote_plus

import httpx

from python_src.tools.base import PythonTool, object_schema


async def web_search(
    query: str,
    *,
    limit: int = 5,
    timeout_seconds: int = 20,
) -> dict[str, Any]:
    url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    try:
        async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": "Mozilla/5.0 (compatible; DeepSeek-Code/0.1; +https://api-docs.deepseek.com)",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.7",
                },
            )
            response.raise_for_status()
    except httpx.HTTPStatusError as error:
        return {
            "query": query,
            "results": [],
            "ok": False,
            "status_code": error.response.status_code,
            "error": f"HTTP {error.response.status_code} while searching",
            "suggestion": "搜索引擎拒绝了自动请求。请换一个查询词、提供网页内容，或稍后重试。",
        }
    except httpx.RequestError as error:
        return {
            "query": query,
            "results": [],
            "ok": False,
            "status_code": None,
            "error": str(error),
            "suggestion": "搜索请求失败。请稍后重试，或提供可访问的信息来源。",
        }
    html = response.text
    results: list[dict[str, str]] = []
    for match in re.finditer(
        r'<a[^>]+class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    ):
        title = re.sub(r"<[^>]+>", "", match.group(2))
        results.append({"title": unescape(title).strip(), "url": unescape(match.group(1))})
        if len(results) >= limit:
            break
    return {
        "query": query,
        "ok": True,
        "results": results,
    }


WebSearchTool = PythonTool(
    name="web_search",
    description="Search the web and return result titles and URLs.",
    parameters=object_schema(
        {
            "query": {"type": "string", "description": "Search query."},
            "limit": {"type": "integer", "description": "Maximum number of results.", "default": 5},
        },
        required=["query"],
    ),
    handler=web_search,
    read_only=True,
)
