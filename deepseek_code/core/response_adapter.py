from __future__ import annotations

import json
from typing import Any

from deepseek_code.core.prompt_builder import tool_calls_from_wire
from deepseek_code.core.types import InternalMessage, InternalResponse, InternalStreamDelta, InternalToolCall


class ResponseAdapter:
    @staticmethod
    def from_completion(response: dict[str, Any]) -> InternalResponse:
        choice = (response.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        return InternalResponse(
            message=InternalMessage(
                role=message.get("role", "assistant"),
                content=message.get("content") or "",
                tool_calls=tool_calls_from_wire(message.get("tool_calls")),
            ),
            finish_reason=choice.get("finish_reason"),
            usage=response.get("usage"),
        )

    @staticmethod
    def from_stream_chunk(chunk: dict[str, Any]) -> InternalStreamDelta:
        choice = (chunk.get("choices") or [{}])[0]
        delta = choice.get("delta") or {}
        return InternalStreamDelta(
            content=delta.get("content") or "",
            tool_calls=tool_calls_from_wire(delta.get("tool_calls")),
            finish_reason=choice.get("finish_reason"),
            usage=chunk.get("usage"),
        )


class StreamingToolCallAccumulator:
    def __init__(self) -> None:
        self._calls: dict[int, dict[str, Any]] = {}

    def add_delta(self, raw_calls: list[dict[str, Any]] | None) -> None:
        for raw in raw_calls or []:
            index = int(raw.get("index", len(self._calls)))
            item = self._calls.setdefault(
                index,
                {"id": "", "type": "function", "function": {"name": "", "arguments": ""}},
            )
            if raw.get("id"):
                item["id"] = raw["id"]
            if raw.get("type"):
                item["type"] = raw["type"]
            fn = raw.get("function") or {}
            if fn.get("name"):
                item["function"]["name"] += fn["name"]
            if fn.get("arguments"):
                item["function"]["arguments"] += fn["arguments"]

    def complete_calls(self) -> list[InternalToolCall]:
        calls: list[InternalToolCall] = []
        for raw in [self._calls[i] for i in sorted(self._calls)]:
            fn = raw.get("function") or {}
            args: dict[str, Any] | str
            try:
                args = json.loads(fn.get("arguments") or "{}")
            except json.JSONDecodeError:
                args = fn.get("arguments") or ""
            calls.append(
                InternalToolCall(
                    id=raw.get("id", ""),
                    type=raw.get("type", "function"),
                    name=fn.get("name", ""),
                    arguments=args,
                )
            )
        return calls
