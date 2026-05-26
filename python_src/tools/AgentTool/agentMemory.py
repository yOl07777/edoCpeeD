from __future__ import annotations

from pathlib import Path
from typing import Any

from ._registry import config_home, cwd, normalize_agent_type

AgentMemoryScope = str


async def getAgentMemoryDir(*args: Any, **kwargs: Any) -> str:
    scope = str(kwargs.get("scope") or (args[0] if args else "user"))
    base = {"project": cwd() / ".deepseek" / "agent-memory", "local": cwd() / ".deepseek" / "agent-memory"}.get(scope, config_home() / "agent-memory")
    return str(base)


async def getAgentMemoryEntrypoint(*args: Any, **kwargs: Any) -> str:
    agent_type = normalize_agent_type(str(kwargs.get("agentType") or (args[0] if args else "agent")))
    scope = str(kwargs.get("scope") or (args[1] if len(args) > 1 else "user"))
    return str(Path(await getAgentMemoryDir(scope)) / f"{agent_type}.md")


async def getMemoryScopeDisplay(*args: Any, **kwargs: Any) -> str:
    scope = str(kwargs.get("scope") or (args[0] if args else "user"))
    return {"user": "User memory", "project": "Project memory", "local": "Local memory"}.get(scope, scope)


async def isAgentMemoryPath(*args: Any, **kwargs: Any) -> bool:
    path = Path(str(kwargs.get("path") or (args[0] if args else ""))).resolve()
    roots = [Path(await getAgentMemoryDir(scope)).resolve() for scope in ("user", "project", "local")]
    return any(root == path or root in path.parents for root in roots)


async def loadAgentMemoryPrompt(*args: Any, **kwargs: Any) -> str:
    agent_type = str(kwargs.get("agentType") or (args[0] if args else "agent"))
    scope = str(kwargs.get("scope") or (args[1] if len(args) > 1 else "user"))
    path = Path(await getAgentMemoryEntrypoint(agent_type, scope))
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


__all__ = ["AgentMemoryScope", "getAgentMemoryDir", "getAgentMemoryEntrypoint", "getMemoryScopeDisplay", "isAgentMemoryPath", "loadAgentMemoryPrompt"]
