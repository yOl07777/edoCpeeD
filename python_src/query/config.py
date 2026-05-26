"""Immutable query configuration snapshot."""

from __future__ import annotations

import os
from typing import Any

try:
    from python_src.bootstrap.state import getSessionId
except Exception:  # pragma: no cover - defensive import fallback
    getSessionId = None  # type: ignore[assignment]


def _env_truthy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "on"}


def _session_id() -> str:
    if callable(getSessionId):
        try:
            return str(getSessionId())
        except Exception:
            pass
    return os.getenv("DEEPSEEK_SESSION_ID") or "local-session"


def buildQueryConfig(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    """Build a DeepSeek-oriented query config snapshot."""

    return {
        "sessionId": _session_id(),
        "gates": {
            "streamingToolExecution": not _env_truthy(os.getenv("DEEPSEEK_DISABLE_STREAMING_TOOL_EXECUTION")),
            "emitToolUseSummaries": _env_truthy(
                os.getenv("DEEPSEEK_CODE_EMIT_TOOL_USE_SUMMARIES")
                or os.getenv("CLAUDE_CODE_EMIT_TOOL_USE_SUMMARIES")
            ),
            "isAnt": os.getenv("USER_TYPE") == "ant",
            "fastModeEnabled": not _env_truthy(
                os.getenv("DEEPSEEK_CODE_DISABLE_FAST_MODE") or os.getenv("CLAUDE_CODE_DISABLE_FAST_MODE")
            ),
        },
    }


__all__ = ["buildQueryConfig"]
