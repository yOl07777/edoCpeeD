from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from deepseek_code.core.types import InternalToolCall
from python_src.tools import build_default_tool_registry


class StreamingToolExecutor:
    def __init__(self, registry: Any | None = None) -> None:
        self.registry = registry or build_default_tool_registry()

    async def execute(self, call: InternalToolCall | dict[str, Any]) -> dict[str, Any]:
        tool_call = call if isinstance(call, InternalToolCall) else InternalToolCall(
            id=str(call.get("id", "call")),
            name=str(call.get("name")),
            arguments=call.get("arguments") or {},
        )
        result = await self.registry.call(tool_call)
        return {"role": result.role, "tool_call_id": result.tool_call_id, "content": result.content}

    async def stream(self, call: InternalToolCall | dict[str, Any]) -> AsyncIterator[dict[str, Any]]:
        yield {"event": "tool_start", "call": call}
        result = await self.execute(call)
        yield {"event": "tool_result", "result": result}
