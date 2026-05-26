"""Prompt text for WebFetchTool."""

from __future__ import annotations

from typing import Any

WEB_FETCH_TOOL_NAME = "web_fetch"
DESCRIPTION = (
    "Fetch a URL and return readable text content. Use this only for user-approved URLs "
    "or public documentation pages, and summarize rather than copying long passages."
)


async def makeSecondaryModelPrompt(*args: Any, **kwargs: Any) -> str:
    url = kwargs.get("url") or (args[0] if args else "")
    prompt = kwargs.get("prompt") or kwargs.get("question") or "Summarize the fetched page."
    return f"URL: {url}\nTask: {prompt}\nReturn a concise answer grounded in the fetched content."


__all__ = ["DESCRIPTION", "WEB_FETCH_TOOL_NAME", "makeSecondaryModelPrompt"]
