"""In-memory exporter used by first-party analytics shims."""

from __future__ import annotations

from typing import Any


class FirstPartyEventLoggingExporter:
    """Small exporter that stores events locally and optionally forwards them."""

    def __init__(self, sink: Any | None = None) -> None:
        self.sink = sink
        self.events: list[dict[str, Any]] = []
        self.closed = False

    async def export(self, events: list[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
        if self.closed:
            return {"exported": 0, "closed": True}
        batch = events if isinstance(events, list) else [events]
        self.events.extend(batch)
        if self.sink:
            result = self.sink(batch)
            if hasattr(result, "__await__"):
                await result
        return {"exported": len(batch), "closed": False}

    async def shutdown(self) -> dict[str, Any]:
        self.closed = True
        return {"closed": True, "events": len(self.events)}

    async def forceFlush(self) -> dict[str, Any]:
        return {"flushed": len(self.events)}
