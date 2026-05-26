"""SSE transport helpers for CCR v2 style streams."""

from __future__ import annotations

import json
from typing import Any

from .WebSocketTransport import WebSocketTransport


def parseSSEFrames(chunk: str) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    for raw_frame in chunk.replace("\r\n", "\n").split("\n\n"):
        if not raw_frame.strip():
            continue
        event = "message"
        data_lines: list[str] = []
        frame_id: str | None = None
        for line in raw_frame.split("\n"):
            if not line or line.startswith(":"):
                continue
            field, _, value = line.partition(":")
            value = value[1:] if value.startswith(" ") else value
            if field == "event":
                event = value
            elif field == "data":
                data_lines.append(value)
            elif field == "id":
                frame_id = value
        data_raw = "\n".join(data_lines)
        if not data_lines:
            continue
        try:
            data: Any = json.loads(data_raw) if data_raw else None
        except ValueError:
            data = data_raw
        frame = {"event": event, "data": data}
        if frame_id is not None:
            frame["id"] = frame_id
        frames.append(frame)
    return frames


class SSETransport(WebSocketTransport):
    kind = "sse"

    def feed_sse(self, chunk: str) -> None:
        for frame in parseSSEFrames(chunk):
            if self.on_data and frame.get("data") is not None:
                self.on_data(json.dumps(frame["data"]) if not isinstance(frame["data"], str) else frame["data"])
