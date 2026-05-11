"""
Python migration draft for `src/utils/ultraplan/ccrSession.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

ULTRAPLAN_TELEPORT_SENTINEL: Any = None

class ExitPlanModeScanner:
    """Migrated placeholder for TypeScript class `ExitPlanModeScanner`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

class UltraplanPollError:
    """Migrated placeholder for TypeScript class `UltraplanPollError`."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.args = args
        self.kwargs = kwargs

async def pollForApprovedExitPlanMode(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `pollForApprovedExitPlanMode`."""
    raise NotImplementedError(
        "utils.ultraplan.ccrSession.pollForApprovedExitPlanMode still needs business-logic migration"
    )
