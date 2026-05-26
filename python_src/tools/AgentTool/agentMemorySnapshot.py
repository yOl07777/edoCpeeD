from __future__ import annotations

from typing import Any

from ._registry import MEMORY_SNAPSHOTS, hash_text, normalize_agent_type


async def checkAgentMemorySnapshot(*args: Any, **kwargs: Any) -> dict[str, Any]:
    agent_type = normalize_agent_type(str(kwargs.get("agentType") or (args[0] if args else "agent")))
    content = str(kwargs.get("content") or (args[1] if len(args) > 1 else ""))
    current = hash_text(content)
    previous = MEMORY_SNAPSHOTS.get(agent_type, {}).get("hash")
    return {"agentType": agent_type, "changed": previous != current, "hash": current, "previousHash": previous}


async def initializeFromSnapshot(*args: Any, **kwargs: Any) -> dict[str, Any]:
    agent_type = normalize_agent_type(str(kwargs.get("agentType") or (args[0] if args else "agent")))
    content = str(kwargs.get("content") or (args[1] if len(args) > 1 else ""))
    snapshot = {"agentType": agent_type, "hash": hash_text(content), "content": content}
    MEMORY_SNAPSHOTS[agent_type] = snapshot
    return snapshot


async def requestSnapshotRefresh(*args: Any, **kwargs: Any) -> dict[str, Any]:
    agent_type = normalize_agent_type(str(kwargs.get("agentType") or (args[0] if args else "agent")))
    MEMORY_SNAPSHOTS.setdefault(agent_type, {})["refreshRequested"] = True
    return {"agentType": agent_type, "refreshRequested": True}


async def snapshotUpdatePending(*args: Any, **kwargs: Any) -> bool:
    agent_type = normalize_agent_type(str(kwargs.get("agentType") or (args[0] if args else "agent")))
    return bool(MEMORY_SNAPSHOTS.get(agent_type, {}).get("refreshRequested"))


async def updateSnapshot(*args: Any, **kwargs: Any) -> dict[str, Any]:
    snapshot = await initializeFromSnapshot(*args, **kwargs)
    snapshot["refreshRequested"] = False
    return snapshot


__all__ = ["checkAgentMemorySnapshot", "initializeFromSnapshot", "requestSnapshotRefresh", "snapshotUpdatePending", "updateSnapshot"]
