"""
Python migration draft for `src/services/voiceStreamSTT.ts`.

This file was generated from the TypeScript source to preserve the
module boundary while the runtime implementation is migrated.
Claude/Anthropic model calls should be routed through `deepseek_code`.
"""

from __future__ import annotations

from typing import Any

FINALIZE_TIMEOUTS_MS: Any = None

async def connectVoiceStream(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `connectVoiceStream`."""
    raise NotImplementedError(
        "services.voiceStreamSTT.connectVoiceStream still needs business-logic migration"
    )

async def isVoiceStreamAvailable(*args: Any, **kwargs: Any) -> Any:
    """Migrated placeholder for TypeScript function `isVoiceStreamAvailable`."""
    raise NotImplementedError(
        "services.voiceStreamSTT.isVoiceStreamAvailable still needs business-logic migration"
    )
