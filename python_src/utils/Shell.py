"""
Python migration draft for `src/utils/Shell.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

getPsProvider: Any = None
getShellConfig: Any = None

async def exec(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `exec`."""
    raise NotImplementedError(
        "utils.Shell.exec still needs business-logic migration"
    )

async def findSuitableShell(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `findSuitableShell`."""
    raise NotImplementedError(
        "utils.Shell.findSuitableShell still needs business-logic migration"
    )

async def setCwd(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `setCwd`."""
    raise NotImplementedError(
        "utils.Shell.setCwd still needs business-logic migration"
    )
