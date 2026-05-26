from __future__ import annotations

from typing import Any


async def startAgentSummarization(agent: dict[str, Any], messages: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    payload = messages or agent.get("messages") or []
    recent = payload[-5:]
    summary = "\n".join(f"- {m.get('role', 'agent')}: {str(m.get('content', ''))[:300]}" for m in recent)
    return {
        "agent_id": agent.get("id"),
        "agent_name": agent.get("name"),
        "message_count": len(payload),
        "summary": summary,
    }
