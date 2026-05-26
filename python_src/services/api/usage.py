"""Local usage aggregation helpers."""

from __future__ import annotations

from typing import Any

from .emptyUsage import EMPTY_USAGE


async def fetchUtilization(records: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Aggregate token usage records without calling an external service."""

    total = dict(EMPTY_USAGE)
    for record in records or []:
        usage = record.get("usage", record)
        input_tokens = int(usage.get("input_tokens", usage.get("prompt_tokens", 0)) or 0)
        output_tokens = int(usage.get("output_tokens", usage.get("completion_tokens", 0)) or 0)
        total["input_tokens"] += input_tokens
        total["output_tokens"] += output_tokens
        total["cache_creation_input_tokens"] += int(usage.get("cache_creation_input_tokens", 0) or 0)
        total["cache_read_input_tokens"] += int(usage.get("cache_read_input_tokens", 0) or 0)
        total["total_tokens"] += int(usage.get("total_tokens", input_tokens + output_tokens) or 0)
    return {"usage": total, "record_count": len(records or [])}
