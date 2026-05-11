"""
Python migration draft for `src/utils/computerUse/common.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

CLI_CU_CAPABILITIES: Any = None
CLI_HOST_BUNDLE_ID: Any = None
COMPUTER_USE_MCP_SERVER_NAME: Any = None

async def getTerminalBundleId(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getTerminalBundleId`."""
    raise NotImplementedError(
        "utils.computerUse.common.getTerminalBundleId still needs business-logic migration"
    )

async def isComputerUseMCPServer(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isComputerUseMCPServer`."""
    raise NotImplementedError(
        "utils.computerUse.common.isComputerUseMCPServer still needs business-logic migration"
    )
