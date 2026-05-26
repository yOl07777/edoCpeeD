"""Diagnostic event tracking."""

from __future__ import annotations

import time
from typing import Any


class DiagnosticTrackingService:
    def __init__(self) -> None:
        self.events: list[dict[str, Any]] = []

    async def track(self, name: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        event = {"name": name, "payload": payload or {}, "timestamp": time.time()}
        self.events.append(event)
        return event

    async def getEvents(self, name: str | None = None) -> list[dict[str, Any]]:
        if name is None:
            return list(self.events)
        return [event for event in self.events if event["name"] == name]

    async def clear(self) -> None:
        self.events.clear()


diagnosticTracker = DiagnosticTrackingService()
