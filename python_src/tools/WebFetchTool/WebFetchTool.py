from __future__ import annotations

import re
from typing import Any

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
    async with httpx.AsyncClient(timeout=timeout_seconds, follow_redirects=True) as client:
        response = await client.get(url, headers={"User-Agent": "deepseek-code/0.1"})
        response.raise_for_status()
    content_type = response.headers.get("content-type", "")
    text = response.text
    if "html" in content_type:
        text = _html_to_text(text)
    return {
        "url": str(response.url),
        "status_code": response.status_code,
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
