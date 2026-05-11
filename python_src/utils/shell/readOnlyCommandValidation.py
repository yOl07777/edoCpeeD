"""
Python migration draft for `src/utils/shell/readOnlyCommandValidation.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

DOCKER_READ_ONLY_COMMANDS: Any = None
EXTERNAL_READONLY_COMMANDS: Any = None
FLAG_PATTERN: Any = None
GH_READ_ONLY_COMMANDS: Any = None
GIT_READ_ONLY_COMMANDS: Any = None
PYRIGHT_READ_ONLY_COMMANDS: Any = None
RIPGREP_READ_ONLY_COMMANDS: Any = None

async def containsVulnerableUncPath(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `containsVulnerableUncPath`."""
    raise NotImplementedError(
        "utils.shell.readOnlyCommandValidation.containsVulnerableUncPath still needs business-logic migration"
    )

async def validateFlagArgument(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `validateFlagArgument`."""
    raise NotImplementedError(
        "utils.shell.readOnlyCommandValidation.validateFlagArgument still needs business-logic migration"
    )

async def validateFlags(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `validateFlags`."""
    raise NotImplementedError(
        "utils.shell.readOnlyCommandValidation.validateFlags still needs business-logic migration"
    )
