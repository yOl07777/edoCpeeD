"""
Python migration draft for `src/utils/fingerprint.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

FINGERPRINT_SALT: Any = None

async def computeFingerprint(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `computeFingerprint`."""
    raise NotImplementedError(
        "utils.fingerprint.computeFingerprint still needs business-logic migration"
    )

async def computeFingerprintFromMessages(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `computeFingerprintFromMessages`."""
    raise NotImplementedError(
        "utils.fingerprint.computeFingerprintFromMessages still needs business-logic migration"
    )

async def extractFirstMessageText(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `extractFirstMessageText`."""
    raise NotImplementedError(
        "utils.fingerprint.extractFirstMessageText still needs business-logic migration"
    )
