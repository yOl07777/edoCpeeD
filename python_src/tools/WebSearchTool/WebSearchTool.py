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
    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "deepseek-code/0.1"})
        response.raise_for_status()
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
