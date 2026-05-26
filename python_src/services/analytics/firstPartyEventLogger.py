"""First-party analytics logger shim."""

from __future__ import annotations

import hashlib
import os
from typing import Any

from .firstPartyEventLoggingExporter import FirstPartyEventLoggingExporter
from .metadata import to1PEventFormat

_EXPORTER: FirstPartyEventLoggingExporter | None = None
_CONFIG: dict[str, Any] = {}


async def getEventSamplingConfig(config: dict[str, Any] | None = None) -> dict[str, Any]:
    source = config or _CONFIG
    return {"sample_rate": float(source.get("sample_rate", source.get("sampleRate", 1.0)))}


async def initialize1PEventLogging(config: dict[str, Any] | None = None) -> dict[str, Any]:
    global _EXPORTER, _CONFIG
    _CONFIG = dict(config or {})
    _EXPORTER = FirstPartyEventLoggingExporter(_CONFIG.get("sink"))
    return {"enabled": await is1PEventLoggingEnabled(_CONFIG)}


async def is1PEventLoggingEnabled(config: dict[str, Any] | None = None) -> bool:
    source = config or _CONFIG
    if "enabled" in source:
        return bool(source["enabled"])
    disabled = os.getenv("DEEPSEEK_DISABLE_1P_EVENTS")
    return str(disabled).lower() not in {"1", "true", "yes", "on"}


async def shouldSampleEvent(event_name: str, config: dict[str, Any] | None = None) -> bool:
    sample_rate = (await getEventSamplingConfig(config))["sample_rate"]
    if sample_rate >= 1:
        return True
    if sample_rate <= 0:
        return False
    digest = hashlib.sha256(str(event_name).encode("utf-8")).hexdigest()
    bucket = int(digest[:8], 16) / 0xFFFFFFFF
    return bucket < sample_rate


async def logEventTo1P(event_name: str, metadata: dict[str, Any] | None = None) -> dict[str, Any] | None:
    global _EXPORTER
    if not await is1PEventLoggingEnabled():
        return None
    if not await shouldSampleEvent(event_name):
        return None
    if _EXPORTER is None:
        await initialize1PEventLogging()
    event = await to1PEventFormat(event_name, metadata)
    await _EXPORTER.export(event)  # type: ignore[union-attr]
    return event


async def logGrowthBookExperimentTo1P(experiment: str, value: Any = None) -> dict[str, Any] | None:
    return await logEventTo1P("growthbook_experiment", {"experiment": experiment, "value": value})


async def reinitialize1PEventLoggingIfConfigChanged(config: dict[str, Any]) -> dict[str, Any]:
    if dict(config) != _CONFIG:
        return await initialize1PEventLogging(config)
    return {"enabled": await is1PEventLoggingEnabled(_CONFIG), "unchanged": True}


async def shutdown1PEventLogging() -> dict[str, Any]:
    global _EXPORTER
    if _EXPORTER is None:
        return {"closed": True, "events": 0}
    result = await _EXPORTER.shutdown()
    _EXPORTER = None
    return result
