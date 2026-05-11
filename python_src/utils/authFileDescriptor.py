"""
Python migration draft for `src/utils/authFileDescriptor.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

CCR_API_KEY_PATH: Any = None
CCR_OAUTH_TOKEN_PATH: Any = None
CCR_SESSION_INGRESS_TOKEN_PATH: Any = None

async def getApiKeyFromFileDescriptor(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getApiKeyFromFileDescriptor`."""
    raise NotImplementedError(
        "utils.authFileDescriptor.getApiKeyFromFileDescriptor still needs business-logic migration"
    )

async def getOAuthTokenFromFileDescriptor(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getOAuthTokenFromFileDescriptor`."""
    raise NotImplementedError(
        "utils.authFileDescriptor.getOAuthTokenFromFileDescriptor still needs business-logic migration"
    )

async def maybePersistTokenForSubprocesses(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `maybePersistTokenForSubprocesses`."""
    raise NotImplementedError(
        "utils.authFileDescriptor.maybePersistTokenForSubprocesses still needs business-logic migration"
    )

async def readTokenFromWellKnownFile(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `readTokenFromWellKnownFile`."""
    raise NotImplementedError(
        "utils.authFileDescriptor.readTokenFromWellKnownFile still needs business-logic migration"
    )
