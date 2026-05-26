from __future__ import annotations

from typing import Any


_VOICE_STATE: dict[str, Any] = {"enabled": False, "listening": False, "transcript": "", "provider": "deepseek"}


async def VoiceProvider(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    _VOICE_STATE.update({key: value for key, value in kwargs.items() if key in {"enabled", "listening", "transcript"}})
    return dict(_VOICE_STATE)


async def useGetVoiceState(*_args: Any, **_kwargs: Any) -> dict[str, Any]:
    return dict(_VOICE_STATE)


async def useSetVoiceState(*_args: Any, **_kwargs: Any):
    async def setter(**updates: Any) -> dict[str, Any]:
        _VOICE_STATE.update({key: value for key, value in updates.items() if key in {"enabled", "listening", "transcript"}})
        return dict(_VOICE_STATE)

    return setter


async def useVoiceState(*_args: Any, **kwargs: Any) -> dict[str, Any]:
    if kwargs:
        await VoiceProvider(**kwargs)
    return dict(_VOICE_STATE)


__all__ = ["VoiceProvider", "useGetVoiceState", "useSetVoiceState", "useVoiceState"]
