"""Agent listing handler."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _format_agent(agent: dict[str, Any]) -> str:
    parts = [str(agent.get("agentType") or agent.get("name") or "agent")]
    if agent.get("model"):
        parts.append(f"model={agent['model']}")
    if agent.get("source"):
        parts.append(f"source={agent['source']}")
    return "  - " + " ".join(parts)


def _load_agents_from_dir(path: Path, source: str) -> list[dict[str, Any]]:
    agents: list[dict[str, Any]] = []
    if not path.exists():
        return agents
    for file in sorted(path.glob("*.json")):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(data, dict):
            data.setdefault("name", file.stem)
            data.setdefault("source", source)
            agents.append(data)
    return agents


async def agentsHandler(cwd: str | None = None, *, json_output: bool = False) -> dict[str, Any] | str:
    root = Path(cwd or ".").resolve()
    agents = []
    agents.extend(_load_agents_from_dir(root / ".deepcode" / "agents", "project"))
    agents.extend(_load_agents_from_dir(Path.home() / ".deepcode" / "agents", "user"))
    if json_output:
        return {"agents": agents}
    if not agents:
        return "No agents configured."
    groups: dict[str, list[dict[str, Any]]] = {}
    for agent in agents:
        groups.setdefault(str(agent.get("source", "unknown")), []).append(agent)
    lines: list[str] = []
    for source, items in groups.items():
        lines.append(f"{source}:")
        lines.extend(_format_agent(agent) for agent in items)
    return "\n".join(lines)
