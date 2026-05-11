"""
Python migration draft for `src/tasks/stopTask.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

class StopTaskError:
    """Migrated placeholder for TypeScript class `StopTaskError`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

async def stopTask(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `stopTask`."""
    raise NotImplementedError(
        "tasks.stopTask.stopTask still needs business-logic migration"
    )
