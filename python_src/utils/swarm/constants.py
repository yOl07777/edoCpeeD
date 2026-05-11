"""
Python migration draft for `src/utils/swarm/constants.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

HIDDEN_SESSION_NAME: Any = None
PLAN_MODE_REQUIRED_ENV_VAR: Any = None
SWARM_SESSION_NAME: Any = None
SWARM_VIEW_WINDOW_NAME: Any = None
TEAMMATE_COLOR_ENV_VAR: Any = None
TEAMMATE_COMMAND_ENV_VAR: Any = None
TEAM_LEAD_NAME: Any = None
TMUX_COMMAND: Any = None

async def getSwarmSocketName(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `getSwarmSocketName`."""
    raise NotImplementedError(
        "utils.swarm.constants.getSwarmSocketName still needs business-logic migration"
    )
