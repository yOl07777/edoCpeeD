from __future__ import annotations

from typing import Any

from ._basic import first_mapping, pick


async def VoiceKeybindingHandler(*args: Any, **kwargs: Any) -> Any:
    return await useVoiceKeybindingHandler(*args, **kwargs)

async def useVoiceIntegration(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    enabled = bool(pick(options, "enabled", default=False))
    keybinding = str(pick(options, "keybinding", default="ctrl+v"))
    return {"provider": "deepseek", "enabled": enabled, "keybinding": keybinding, "status": "ready" if enabled else "disabled"}

async def useVoiceKeybindingHandler(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    key = str(pick(options, "key", default=""))
    expected = str(pick(options, "keybinding", default="ctrl+v"))
    return {"provider": "deepseek", "handled": key == expected, "action": "toggle_voice" if key == expected else None}
