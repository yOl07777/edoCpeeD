"""Convenience query helpers for DeepSeek-backed conversations."""

from __future__ import annotations

from typing import Any

from python_src.QueryEngine import QueryEngine


async def query(prompt: str, **kwargs: Any) -> Any:
    async with QueryEngine(**{k: v for k, v in kwargs.items() if k in {"model", "client", "tool_registry", "system_prompt", "config"}}) as engine:
        run_kwargs = {k: v for k, v in kwargs.items() if k not in {"model", "client", "tool_registry", "system_prompt", "config"}}
        return await engine.query(prompt, **run_kwargs)


async def streamQuery(prompt: str, **kwargs: Any) -> list[Any]:
    chunks: list[Any] = []
    async with QueryEngine(**{k: v for k, v in kwargs.items() if k in {"model", "client", "tool_registry", "system_prompt", "config"}}) as engine:
        run_kwargs = {k: v for k, v in kwargs.items() if k not in {"model", "client", "tool_registry", "system_prompt", "config"}}
        async for chunk in engine.stream(prompt, **run_kwargs):
            chunks.append(chunk)
    return chunks


__all__ = ["QueryEngine", "query", "streamQuery"]
