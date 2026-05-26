"""Offline token estimation helpers for DeepSeek-compatible requests."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

_BYTES_PER_TOKEN = {
    "py": 3.2,
    "ts": 3.2,
    "tsx": 3.2,
    "js": 3.2,
    "jsx": 3.2,
    "json": 2.7,
    "md": 3.8,
    "txt": 4.0,
    "yaml": 3.2,
    "yml": 3.2,
    "html": 3.0,
    "css": 3.0,
}


def _stringify(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=str)


async def bytesPerTokenForFileType(file_type: str | None = None) -> float:
    ext = str(file_type or "").lower().lstrip(".")
    return _BYTES_PER_TOKEN.get(ext, 4.0)


async def roughTokenCountEstimation(text: Any) -> int:
    """Estimate tokens using a mixed ASCII/CJK heuristic."""

    value = _stringify(text)
    if not value:
        return 0
    cjk = sum(1 for ch in value if "\u4e00" <= ch <= "\u9fff")
    non_cjk = len(value) - cjk
    return max(1, math.ceil(cjk * 0.9 + non_cjk / 4))


async def roughTokenCountEstimationForFileType(content: Any, file_type: str | None = None) -> int:
    value = _stringify(content)
    bytes_per_token = await bytesPerTokenForFileType(file_type)
    return max(1, math.ceil(len(value.encode("utf-8")) / bytes_per_token)) if value else 0


async def roughTokenCountEstimationForMessage(message: dict[str, Any] | str) -> int:
    if isinstance(message, str):
        return await roughTokenCountEstimation(message)
    overhead = 4
    content = message.get("content", "")
    if isinstance(content, list):
        total = overhead
        for item in content:
            if isinstance(item, dict) and item.get("type") in {"image", "image_url"}:
                total += 85
            else:
                total += await roughTokenCountEstimation(item)
        return total
    return overhead + await roughTokenCountEstimation(content)


async def roughTokenCountEstimationForMessages(messages: list[dict[str, Any]]) -> int:
    return sum([await roughTokenCountEstimationForMessage(message) for message in messages]) + 3


async def countTokensWithAPI(text: Any, *_args: Any, **_kwargs: Any) -> int:
    """Compatibility wrapper; DeepSeek has no local token-count endpoint here."""

    return await roughTokenCountEstimation(text)


async def countMessagesTokensWithAPI(messages: list[dict[str, Any]], *_args: Any, **_kwargs: Any) -> int:
    return await roughTokenCountEstimationForMessages(messages)


async def countTokensViaHaikuFallback(text: Any, *_args: Any, **_kwargs: Any) -> int:
    """Legacy fallback name retained; uses the same DeepSeek-oriented heuristic."""

    return await roughTokenCountEstimation(text)
