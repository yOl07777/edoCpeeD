from __future__ import annotations

from typing import Any

from python_src.services.tools.StreamingToolExecutor import StreamingToolExecutor


async def executeToolCalls(calls: list[dict[str, Any]], *, executor: StreamingToolExecutor | None = None) -> list[dict[str, Any]]:
    runner = executor or StreamingToolExecutor()
    results = []
    for call in calls:
        results.append(await runner.execute(call))
    return results


async def streamToolCall(call: dict[str, Any], *, executor: StreamingToolExecutor | None = None) -> list[dict[str, Any]]:
    runner = executor or StreamingToolExecutor()
    return [event async for event in runner.stream(call)]
