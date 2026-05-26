"""Local `/voice` command shim."""

from __future__ import annotations

from typing import Any

from python_src.utils.auth import isAnthropicAuthEnabled
from python_src.utils.config import getGlobalConfig, saveGlobalConfig
from python_src.voice.voiceModeEnabled import isVoiceModeEnabled


async def call(*_args: Any, **_kwargs: Any) -> dict[str, str]:
    if not isVoiceModeEnabled():
        if not await isAnthropicAuthEnabled():
            return {"type": "text", "value": "Voice mode requires DeepSeek authentication. Please run /login first."}
        return {"type": "text", "value": "Voice mode is not available in this environment."}

    config = await getGlobalConfig()
    enabled = bool(config.get("voiceEnabled"))
    next_enabled = not enabled
    await saveGlobalConfig({"voiceEnabled": next_enabled})
    return {
        "type": "text",
        "value": (
            "Voice mode enabled. Hold the configured push-to-talk shortcut to record."
            if next_enabled
            else "Voice mode disabled."
        ),
    }
