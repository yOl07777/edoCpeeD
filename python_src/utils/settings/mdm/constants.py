"""
Python migration draft for `src/utils/settings/mdm/constants.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

MACOS_PREFERENCE_DOMAIN: Any = None
MDM_SUBPROCESS_TIMEOUT_MS: Any = None
PLUTIL_ARGS_PREFIX: Any = None
PLUTIL_PATH: Any = None
WINDOWS_REGISTRY_KEY_PATH_HKCU: Any = None
WINDOWS_REGISTRY_KEY_PATH_HKLM: Any = None
WINDOWS_REGISTRY_VALUE_NAME: Any = None

async def getMacOSPlistPaths(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getMacOSPlistPaths`."""
    raise NotImplementedError(
        "utils.settings.mdm.constants.getMacOSPlistPaths still needs business-logic migration"
    )
