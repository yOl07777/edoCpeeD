"""Local voice-stream STT shim."""

from __future__ import annotations

import time
from typing import Any, Callable

FINALIZE_TIMEOUTS_MS = {"partial": 500, "final": 1500}


class VoiceStreamConnection:
    def __init__(self, on_transcript: Callable[[dict[str, Any]], Any] | None = None) -> None:
        self.on_transcript = on_transcript
        self.connected = True
        self.events: list[dict[str, Any]] = []

    async def send_audio(self, data: bytes | str, transcript: str | None = None) -> dict[str, Any]:
        event = {
            "type": "transcript",
            "partial": transcript if transcript is not None else "",
            "bytes": len(data if isinstance(data, bytes) else str(data).encode("utf-8")),
            "timestamp": time.time(),
        }
        self.events.append(event)
        if self.on_transcript:
            result = self.on_transcript(event)
            if hasattr(result, "__await__"):
                await result
        return event

    async def close(self) -> dict[str, Any]:
        self.connected = False
        return {"connected": False, "events": len(self.events)}


async def isVoiceStreamAvailable(config: dict[str, Any] | None = None) -> bool:
    if config and "enabled" in config:
        return bool(config["enabled"])
    return True


async def connectVoiceStream(on_transcript: Callable[[dict[str, Any]], Any] | None = None, **_kwargs: Any) -> VoiceStreamConnection:
    return VoiceStreamConnection(on_transcript)
