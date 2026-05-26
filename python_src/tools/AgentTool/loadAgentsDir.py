"""Load local AgentTool definitions from JSON and Markdown files."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ._registry import AGENT_DEFINITIONS, cwd, normalize_agent_type, register_definition


def _parse_scalar(value: str) -> Any:
    text = value.strip().strip('"').strip("'")
    if text.lower() in {"true", "false"}:
        return text.lower() == "true"
    if "," in text:
        return [part.strip() for part in text.split(",") if part.strip()]
    return text


def _frontmatter(text: str) -> tuple[dict[str, Any], str]:
    if not text.startswith("---"):
        return {}, text
    marker = text.find("\n---", 3)
    if marker == -1:
        return {}, text
    meta_text = text[3:marker].strip()
    body = text[marker + 4 :].strip()
    metadata: dict[str, Any] = {}
    for line in meta_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = _parse_scalar(value)
    return metadata, body


def _agent_type_from_path(path: Path) -> str:
    return normalize_agent_type(path.stem)


def _read_markdown_value(value: Any) -> str:
    if isinstance(value, Path):
        return value.read_text(encoding="utf-8")
    if isinstance(value, str) and "\n" not in value and len(value) < 260:
        path = Path(value)
        if path.exists():
            return path.read_text(encoding="utf-8")
    return str(value)


async def clearAgentDefinitionsCache(*args: Any, **kwargs: Any) -> None:
    keep_builtins = bool(kwargs.get("keepBuiltIns") or kwargs.get("keep_builtins"))
    if keep_builtins:
        for key in [k for k, v in AGENT_DEFINITIONS.items() if v.get("source") != "built-in"]:
            AGENT_DEFINITIONS.pop(key, None)
    else:
        AGENT_DEFINITIONS.clear()


async def hasRequiredMcpServers(*args: Any, **kwargs: Any) -> bool:
    agent = args[0] if args else kwargs.get("agent", {})
    required = agent.get("mcpServers") if isinstance(agent, dict) else None
    available = set(kwargs.get("availableServers") or kwargs.get("available_servers") or required or [])
    return all(server in available for server in (required or []))


async def filterAgentsByMcpRequirements(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    agents = list(args[0] if args else kwargs.get("agents", []) or [])
    result = []
    for agent in agents:
        if await hasRequiredMcpServers(agent, **kwargs):
            result.append(agent)
    return result


async def getActiveAgentsFromList(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    agents = list(args[0] if args else kwargs.get("agents", []) or [])
    return [agent for agent in agents if agent.get("enabled", True)]


async def isBuiltInAgent(*args: Any, **kwargs: Any) -> bool:
    agent = args[0] if args else kwargs.get("agent", {})
    return isinstance(agent, dict) and agent.get("source") == "built-in"


async def isCustomAgent(*args: Any, **kwargs: Any) -> bool:
    agent = args[0] if args else kwargs.get("agent", {})
    return isinstance(agent, dict) and agent.get("source") in {"custom", "local", "workspace"}


async def isPluginAgent(*args: Any, **kwargs: Any) -> bool:
    agent = args[0] if args else kwargs.get("agent", {})
    return isinstance(agent, dict) and agent.get("source") == "plugin"


async def parseAgentFromJson(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = args[0] if args else kwargs.get("value", {})
    source_path = Path(kwargs["path"]) if kwargs.get("path") else None
    data = json.loads(value) if isinstance(value, str) else dict(value or {})
    agent_type = data.get("agentType") or data.get("type") or data.get("name") or (source_path.stem if source_path else "agent")
    return register_definition(
        str(agent_type),
        **{
            "name": data.get("name") or str(agent_type).replace("-", " ").title(),
            "description": data.get("description") or data.get("whenToUse", ""),
            "whenToUse": data.get("whenToUse") or data.get("description", ""),
            "instructions": data.get("instructions") or data.get("prompt", ""),
            "source": data.get("source", "custom"),
            "baseDir": str(source_path.parent if source_path else cwd()),
            "tools": data.get("tools", []),
            "mcpServers": data.get("mcpServers", []),
            "enabled": data.get("enabled", True),
        },
    )


async def parseAgentFromMarkdown(*args: Any, **kwargs: Any) -> dict[str, Any]:
    value = args[0] if args else kwargs.get("value", "")
    path = Path(kwargs["path"]) if kwargs.get("path") else None
    text = _read_markdown_value(value)
    metadata, body = _frontmatter(text)
    agent_type = metadata.get("agentType") or metadata.get("type") or metadata.get("name") or (_agent_type_from_path(path) if path else "agent")
    return register_definition(
        str(agent_type),
        name=metadata.get("name") or str(agent_type).replace("-", " ").title(),
        description=metadata.get("description") or metadata.get("whenToUse", ""),
        whenToUse=metadata.get("whenToUse") or metadata.get("description", ""),
        instructions=body,
        source=metadata.get("source", "custom"),
        baseDir=str(path.parent if path else cwd()),
        tools=metadata.get("tools", []),
        mcpServers=metadata.get("mcpServers", []),
        enabled=metadata.get("enabled", True),
        path=str(path) if path else "",
    )


async def parseAgentsFromJson(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    value = args[0] if args else kwargs.get("value", [])
    data = json.loads(value) if isinstance(value, str) else value
    agents = data.get("agents", []) if isinstance(data, dict) else list(data or [])
    return [await parseAgentFromJson(agent, **kwargs) for agent in agents]


async def loadAgentsDir(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    root = Path(args[0] if args else kwargs.get("path", cwd() / ".deepcode" / "agents")).expanduser()
    if not root.exists():
        return []
    agents: list[dict[str, Any]] = []
    for path in sorted(root.rglob("*")):
        if path.suffix.lower() == ".md":
            agents.append(await parseAgentFromMarkdown(path.read_text(encoding="utf-8"), path=str(path)))
        elif path.suffix.lower() == ".json":
            value = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(value, list) or "agents" in value:
                agents.extend(await parseAgentsFromJson(value, path=str(path)))
            else:
                agents.append(await parseAgentFromJson(value, path=str(path)))
    return await getActiveAgentsFromList(await filterAgentsByMcpRequirements(agents, **kwargs))


getAgentDefinitionsWithOverrides = loadAgentsDir


__all__ = [
    "clearAgentDefinitionsCache",
    "filterAgentsByMcpRequirements",
    "getActiveAgentsFromList",
    "getAgentDefinitionsWithOverrides",
    "hasRequiredMcpServers",
    "isBuiltInAgent",
    "isCustomAgent",
    "isPluginAgent",
    "loadAgentsDir",
    "parseAgentFromJson",
    "parseAgentFromMarkdown",
    "parseAgentsFromJson",
]
