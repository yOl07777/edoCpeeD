"""
Python migration draft for `src/utils/platform.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

SUPPORTED_PLATFORMS: Any = None
getLinuxDistroInfo: Any = None
getPlatform: Any = None
getWslVersion: Any = None

async def detectVcs(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `detectVcs`."""
    raise NotImplementedError(
        "utils.platform.detectVcs still needs business-logic migration"
    )
