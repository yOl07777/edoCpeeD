"""
Python migration draft for `src/keybindings/reservedShortcuts.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

MACOS_RESERVED: Any = None
NON_REBINDABLE: Any = None
TERMINAL_RESERVED: Any = None

async def getReservedShortcuts(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getReservedShortcuts`."""
    raise NotImplementedError(
        "keybindings.reservedShortcuts.getReservedShortcuts still needs business-logic migration"
    )

async def normalizeKeyForComparison(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `normalizeKeyForComparison`."""
    raise NotImplementedError(
        "keybindings.reservedShortcuts.normalizeKeyForComparison still needs business-logic migration"
    )
