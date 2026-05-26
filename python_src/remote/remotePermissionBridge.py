"""Permission bridge helpers for remote DeepCode sessions."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def createSyntheticAssistantMessage(request: dict[str, Any], requestId: str) -> dict[str, Any]:
    """Create an assistant tool-use message for a remote permission request."""

    return {
        "type": "assistant",
        "uuid": str(uuid.uuid4()),
        "message": {
            "id": f"remote-{requestId}",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "tool_use",
                    "id": request.get("tool_use_id"),
                    "name": request.get("tool_name"),
                    "input": request.get("input") or {},
                }
            ],
            "model": "",
            "stop_reason": None,
            "stop_sequence": None,
            "container": None,
            "context_management": None,
            "usage": {
                "input_tokens": 0,
                "output_tokens": 0,
                "cache_creation_input_tokens": 0,
                "cache_read_input_tokens": 0,
            },
        },
        "requestId": None,
        "timestamp": _now(),
    }


class ToolStub:
    def __init__(self, toolName: str) -> None:
        self.name = toolName
        self.inputSchema: dict[str, Any] = {}
        self.isMcp = False

    def isEnabled(self) -> bool:
        return True

    def userFacingName(self) -> str:
        return self.name

    def renderToolUseMessage(self, input: dict[str, Any] | None = None) -> str:
        items = list((input or {}).items())
        if not items:
            return ""
        rendered: list[str] = []
        for key, value in items[:3]:
            value_str = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            rendered.append(f"{key}: {value_str}")
        return ", ".join(rendered)

    async def call(self, *_: Any, **__: Any) -> dict[str, str]:
        return {"data": ""}

    async def description(self) -> str:
        return ""

    def prompt(self) -> str:
        return ""

    def isReadOnly(self) -> bool:
        return False

    def needsPermissions(self) -> bool:
        return True


def createToolStub(toolName: str) -> ToolStub:
    return ToolStub(toolName)


__all__ = ["ToolStub", "createSyntheticAssistantMessage", "createToolStub"]
