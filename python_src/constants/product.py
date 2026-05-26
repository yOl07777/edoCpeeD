from __future__ import annotations

import os
from typing import Any


DEEPSEEK_AI_BASE_URL = "https://platform.deepseek.com"
DEEPSEEK_AI_LOCAL_BASE_URL = "http://localhost:3000"
DEEPSEEK_AI_STAGING_BASE_URL = "https://staging.platform.deepseek.com"
PRODUCT_URL = DEEPSEEK_AI_BASE_URL

# Compatibility names for TS-derived imports. Values intentionally point at
# DeepSeek-oriented endpoints instead of Anthropic services.
CLAUDE_AI_BASE_URL = DEEPSEEK_AI_BASE_URL
CLAUDE_AI_LOCAL_BASE_URL = DEEPSEEK_AI_LOCAL_BASE_URL
CLAUDE_AI_STAGING_BASE_URL = DEEPSEEK_AI_STAGING_BASE_URL


async def getClaudeAiBaseUrl(*_args: Any, **_kwargs: Any) -> str:
    return os.getenv("DEEPSEEK_CODE_BASE_URL") or os.getenv("DEEPSEEK_PRODUCT_URL") or DEEPSEEK_AI_BASE_URL


async def getRemoteSessionUrl(session_id: Any = "", *_args: Any, **kwargs: Any) -> str:
    base = str(kwargs.get("base_url") or await getClaudeAiBaseUrl()).rstrip("/")
    session = str(kwargs.get("session_id") or session_id or "").strip()
    if not session:
        return f"{base}/sessions"
    return f"{base}/sessions/{session}"


async def isRemoteSessionLocal(*_args: Any, **kwargs: Any) -> bool:
    base = str(kwargs.get("base_url") or await getClaudeAiBaseUrl()).lower()
    return "localhost" in base or "127.0.0.1" in base


async def isRemoteSessionStaging(*_args: Any, **kwargs: Any) -> bool:
    base = str(kwargs.get("base_url") or await getClaudeAiBaseUrl()).lower()
    return "staging" in base or "dev" in base


__all__ = [
    "CLAUDE_AI_BASE_URL",
    "CLAUDE_AI_LOCAL_BASE_URL",
    "CLAUDE_AI_STAGING_BASE_URL",
    "DEEPSEEK_AI_BASE_URL",
    "DEEPSEEK_AI_LOCAL_BASE_URL",
    "DEEPSEEK_AI_STAGING_BASE_URL",
    "PRODUCT_URL",
    "getClaudeAiBaseUrl",
    "getRemoteSessionUrl",
    "isRemoteSessionLocal",
    "isRemoteSessionStaging",
]
