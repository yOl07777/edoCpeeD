"""Small in-memory VCR helpers for deterministic tests."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Callable

_CASSETTES: dict[str, Any] = {}


def _key(name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
    payload = json.dumps({"name": name, "args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


async def withVCR(name: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    key = _key(name, args, kwargs)
    if key in _CASSETTES:
        return _CASSETTES[key]
    result = func(*args, **kwargs)
    if hasattr(result, "__await__"):
        result = await result
    _CASSETTES[key] = result
    return result


async def withTokenCountVCR(name: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    return await withVCR(f"token-count:{name}", func, *args, **kwargs)


async def clearVCR() -> None:
    _CASSETTES.clear()
