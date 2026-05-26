from __future__ import annotations

import hashlib
import os
from typing import Any


DEEPSEEK_AI_INFERENCE_SCOPE = "deepseek:chat"
DEEPSEEK_AI_PROFILE_SCOPE = "deepseek:profile"
DEEPSEEK_AI_OAUTH_SCOPES = [DEEPSEEK_AI_INFERENCE_SCOPE, DEEPSEEK_AI_PROFILE_SCOPE]
CONSOLE_OAUTH_SCOPES = ["openid", "profile", "email"]
ALL_OAUTH_SCOPES = sorted(set(DEEPSEEK_AI_OAUTH_SCOPES + CONSOLE_OAUTH_SCOPES))
MCP_CLIENT_METADATA_URL = os.getenv("DEEPSEEK_MCP_CLIENT_METADATA_URL", "")
OAUTH_BETA_HEADER = ""

# Compatibility aliases for TS-derived imports.
CLAUDE_AI_INFERENCE_SCOPE = DEEPSEEK_AI_INFERENCE_SCOPE
CLAUDE_AI_PROFILE_SCOPE = DEEPSEEK_AI_PROFILE_SCOPE
CLAUDE_AI_OAUTH_SCOPES = DEEPSEEK_AI_OAUTH_SCOPES


async def fileSuffixForOauthConfig(config: Any = None, *_args: Any, **kwargs: Any) -> str:
    value = kwargs.get("client_id") or kwargs.get("issuer") or config or "deepseek"
    digest = hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:10]
    return f"oauth-{digest}.json"


async def getOauthConfig(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    base = str(kwargs.get("base_url") or os.getenv("DEEPSEEK_OAUTH_BASE_URL") or "https://platform.deepseek.com").rstrip("/")
    client_id = str(kwargs.get("client_id") or os.getenv("DEEPSEEK_OAUTH_CLIENT_ID") or "deepseek-code")
    return {
        "provider": "deepseek",
        "client_id": client_id,
        "authorization_endpoint": f"{base}/oauth/authorize",
        "token_endpoint": f"{base}/oauth/token",
        "scopes": list(kwargs.get("scopes") or DEEPSEEK_AI_OAUTH_SCOPES),
        "metadata_url": MCP_CLIENT_METADATA_URL,
        "file_suffix": await fileSuffixForOauthConfig(client_id),
    }


__all__ = [
    "ALL_OAUTH_SCOPES",
    "CLAUDE_AI_INFERENCE_SCOPE",
    "CLAUDE_AI_OAUTH_SCOPES",
    "CLAUDE_AI_PROFILE_SCOPE",
    "CONSOLE_OAUTH_SCOPES",
    "DEEPSEEK_AI_INFERENCE_SCOPE",
    "DEEPSEEK_AI_OAUTH_SCOPES",
    "DEEPSEEK_AI_PROFILE_SCOPE",
    "MCP_CLIENT_METADATA_URL",
    "OAUTH_BETA_HEADER",
    "fileSuffixForOauthConfig",
    "getOauthConfig",
]
