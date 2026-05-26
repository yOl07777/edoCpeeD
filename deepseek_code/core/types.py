from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

Role = Literal["system", "user", "assistant", "tool"]


@dataclass
class InternalToolCall:
    id: str
    name: str
    arguments: dict[str, Any] | str
    type: str = "function"


@dataclass
class InternalMessage:
    role: Role
    content: str | list[dict[str, Any]] | None
    name: str | None = None
    tool_call_id: str | None = None
    tool_calls: list[InternalToolCall] = field(default_factory=list)
    reasoning_content: str | None = None


@dataclass
class InternalResponse:
    message: InternalMessage
    finish_reason: str | None = None
    usage: dict[str, Any] | None = None


@dataclass
class InternalStreamDelta:
    content: str = ""
    reasoning_content: str = ""
    tool_calls: list[InternalToolCall] = field(default_factory=list)
    finish_reason: str | None = None
    usage: dict[str, Any] | None = None
