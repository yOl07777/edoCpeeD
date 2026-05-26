from __future__ import annotations

import re
from pathlib import Path
from typing import Any


AGENT_COLORS = ["red", "orange", "yellow", "green", "blue", "purple", "pink", "gray"]
AGENT_MODELS = ["deepseek-chat", "deepseek-coder", "deepseek-reasoner"]
AGENT_SOURCES = {
    "userSettings": "User",
    "projectSettings": "Project",
    "localSettings": "Local project",
    "policySettings": "Managed policy",
    "flagSettings": "CLI argument",
    "built-in": "Built-in",
    "plugin": "Plugin",
    "all": "All",
}


def coerce_agent(value: Any = None, **kwargs: Any) -> dict[str, Any]:
    if isinstance(value, dict):
        data = dict(value)
    else:
        data = {}
    data.update({key: val for key, val in kwargs.items() if val is not None})
    agent_type = data.get("agentType") or data.get("identifier") or data.get("name") or "deepseek-agent"
    when = data.get("whenToUse") or data.get("description") or "Use this agent when specialized help is needed."
    prompt = data.get("systemPrompt") or data.get("prompt") or "You are a focused DeepSeek Code subagent."
    source = data.get("source") or data.get("location") or "projectSettings"
    tools = data.get("tools")
    if tools == "":
        tools = []
    return {
        "agentType": str(agent_type),
        "whenToUse": str(when),
        "systemPrompt": str(prompt),
        "source": str(source),
        "tools": tools,
        "color": data.get("color") or "blue",
        "model": data.get("model") or "deepseek-chat",
        "memory": data.get("memory"),
        "effort": data.get("effort"),
        "filename": data.get("filename"),
    }


def slugify_agent_name(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9-]+", "-", text.strip().lower()).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    return slug or "deepseek-agent"


def component_result(component: str, **kwargs: Any) -> dict[str, Any]:
    payload = {"type": component, "provider": "deepseek"}
    payload.update(kwargs)
    return payload


def project_root() -> Path:
    return Path.cwd()

