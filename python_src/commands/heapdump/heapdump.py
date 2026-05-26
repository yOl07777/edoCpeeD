"""Local `/heapdump` command."""

from __future__ import annotations

from typing import Any

from python_src.utils.heapDumpService import performHeapDump


async def call(*_args: Any, **_kwargs: Any) -> dict[str, str]:
    result = await performHeapDump()
    if not result.get("success"):
        return {"type": "text", "value": f"Failed to create heap dump: {result.get('error', 'unknown error')}"}
    return {"type": "text", "value": f"{result.get('heapPath')}\n{result.get('diagPath')}"}
