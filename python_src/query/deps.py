"""Production dependency factory for query orchestration."""

from __future__ import annotations

import uuid
from typing import Any

from python_src.services.api.claude import query_model_streaming


async def _microcompact_messages(messages: Any = None, *_args: Any, **_kwargs: Any) -> Any:
    return messages


async def _auto_compact_if_needed(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return {"compacted": False, "provider": "deepseek"}


def productionDeps(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    """Return concrete DeepSeek-safe dependencies for the Python query loop."""

    return {
        "callModel": query_model_streaming,
        "microcompact": _microcompact_messages,
        "autocompact": _auto_compact_if_needed,
        "uuid": lambda: str(uuid.uuid4()),
    }


__all__ = ["productionDeps"]
