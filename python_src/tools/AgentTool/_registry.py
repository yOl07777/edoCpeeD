"""Shared AgentTool registry for migrated Python shims."""

from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path
from typing import Any

AGENT_DEFINITIONS: dict[str, dict[str, Any]] = {}
AGENT_RUNS: dict[str, dict[str, Any]] = {}
AGENT_COLORS_STATE: dict[str, str] = {}
PENDING_MESSAGES: dict[str, list[Any]] = {}
MEMORY_SNAPSHOTS: dict[str, dict[str, Any]] = {}


def config_home() -> Path:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CODE_HOME")
    return Path(root).expanduser().resolve() if root else (Path.home() / ".deepcode").resolve()


def cwd() -> Path:
    return Path(os.getenv("DEEPCODE_CWD") or os.getcwd()).resolve()


def normalize_agent_type(value: str) -> str:
    text = str(value or "agent").strip().lower().replace(" ", "-").replace("_", "-")
    return "".join(ch for ch in text if ch.isalnum() or ch == "-") or "agent"


def register_definition(agent_type: str, **fields: Any) -> dict[str, Any]:
    normalized = normalize_agent_type(agent_type)
    definition = {
        "agentType": normalized,
        "whenToUse": fields.pop("whenToUse", fields.get("description", "")),
        "source": fields.pop("source", "local"),
        "baseDir": fields.pop("baseDir", ""),
        "tools": fields.pop("tools", []),
        "model": fields.pop("model", None),
        "color": fields.pop("color", None),
        **fields,
    }
    AGENT_DEFINITIONS[normalized] = definition
    return definition


def get_definition(agent_type: str) -> dict[str, Any] | None:
    return AGENT_DEFINITIONS.get(normalize_agent_type(agent_type))


def run_agent(agent_type: str, prompt: str = "", **fields: Any) -> dict[str, Any]:
    definition = get_definition(agent_type) or register_definition(agent_type, source="ad-hoc", whenToUse="Ad-hoc local agent")
    run_id = "agent-run-" + uuid.uuid4().hex[:10]
    run = {
        "id": run_id,
        "runId": run_id,
        "agentType": definition["agentType"],
        "prompt": prompt,
        "status": fields.pop("status", "completed"),
        "messages": [],
        "result": fields.pop("result", f"Dry-run agent {definition['agentType']} accepted the task."),
        **fields,
    }
    AGENT_RUNS[run_id] = run
    return run


def hash_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def reset_registry() -> None:
    AGENT_DEFINITIONS.clear()
    AGENT_RUNS.clear()
    AGENT_COLORS_STATE.clear()
    PENDING_MESSAGES.clear()
    MEMORY_SNAPSHOTS.clear()


__all__ = [
    "AGENT_COLORS_STATE",
    "AGENT_DEFINITIONS",
    "AGENT_RUNS",
    "MEMORY_SNAPSHOTS",
    "PENDING_MESSAGES",
    "config_home",
    "cwd",
    "get_definition",
    "hash_text",
    "normalize_agent_type",
    "register_definition",
    "reset_registry",
    "run_agent",
]
