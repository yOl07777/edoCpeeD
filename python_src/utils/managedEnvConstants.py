"""
Python migration draft for `src/utils/managedEnvConstants.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

DANGEROUS_SHELL_SETTINGS: Any = None
SAFE_ENV_VARS: Any = None

async def isProviderManagedEnvVar(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isProviderManagedEnvVar`."""
    raise NotImplementedError(
        "utils.managedEnvConstants.isProviderManagedEnvVar still needs business-logic migration"
    )
