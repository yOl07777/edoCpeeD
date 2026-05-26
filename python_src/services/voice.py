"""Local voice recording state for the Python migration."""

from __future__ import annotations

import shutil
import time
from typing import Any

_ARECORD_PROBE: bool | None = None
_ALSA_CARDS: list[str] | None = None
_RECORDING: dict[str, Any] | None = None
_MIC_PERMISSION = False


async def _resetAlsaCardsForTesting() -> None:
    global _ALSA_CARDS
    _ALSA_CARDS = None


async def _resetArecordProbeForTesting() -> None:
    global _ARECORD_PROBE
    _ARECORD_PROBE = None


async def checkVoiceDependencies() -> dict[str, Any]:
    """Check for optional local recording tools without requiring them."""

    global _ARECORD_PROBE
    if _ARECORD_PROBE is None:
        _ARECORD_PROBE = shutil.which("arecord") is not None or shutil.which("ffmpeg") is not None
    return {"available": bool(_ARECORD_PROBE), "arecord_or_ffmpeg": bool(_ARECORD_PROBE)}


async def requestMicrophonePermission(force: bool | None = None) -> dict[str, Any]:
    global _MIC_PERMISSION
    if force is not None:
        _MIC_PERMISSION = bool(force)
    else:
        _MIC_PERMISSION = True
    return {"granted": _MIC_PERMISSION}


async def checkRecordingAvailability() -> dict[str, Any]:
    deps = await checkVoiceDependencies()
    return {"available": deps["available"] and _MIC_PERMISSION, "dependencies": deps, "permission": _MIC_PERMISSION}


async def startRecording(session_id: str = "default", **metadata: Any) -> dict[str, Any]:
    global _RECORDING
    permission = await requestMicrophonePermission(metadata.pop("permission", None))
    deps = await checkVoiceDependencies()
    _RECORDING = {
        "recording": True,
        "session_id": session_id,
        "started_at": time.time(),
        "permission": permission["granted"],
        "dependencies": deps,
        "metadata": metadata,
        "chunks": [],
    }
    return dict(_RECORDING)


async def stopRecording(transcript: str | None = None) -> dict[str, Any]:
    global _RECORDING
    if _RECORDING is None:
        return {"recording": False, "duration": 0, "transcript": transcript or ""}
    ended_at = time.time()
    result = {
        **_RECORDING,
        "recording": False,
        "ended_at": ended_at,
        "duration": max(0.0, ended_at - float(_RECORDING.get("started_at", ended_at))),
        "transcript": transcript or "",
    }
    _RECORDING = None
    return result


async def getRecordingState() -> dict[str, Any]:
    return dict(_RECORDING or {"recording": False})
