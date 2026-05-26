from __future__ import annotations

import re
from typing import NewType

SessionId = NewType("SessionId", str)
AgentId = NewType("AgentId", str)

AGENT_ID_PATTERN = re.compile(r"^a(?:.+-)?[0-9a-f]{16}$")


def asSessionId(id: str) -> SessionId:
    return SessionId(str(id))


def asAgentId(id: str) -> AgentId:
    return AgentId(str(id))


def toAgentId(value: str) -> AgentId | None:
    text = str(value)
    return AgentId(text) if AGENT_ID_PATTERN.match(text) else None


__all__ = ["AgentId", "SessionId", "asAgentId", "asSessionId", "toAgentId"]
