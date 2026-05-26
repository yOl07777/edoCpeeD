"""Managed web-connector MCP config shim.

The original TS module fetches Claude.ai managed MCP servers over OAuth. The
DeepSeek/Python migration keeps the same callable surface but avoids implicit
network access. Tests and local runs can inject connector data with
``DEEPCODE_CLAUDEAI_MCP_SERVERS`` or ``DEEPSEEK_MANAGED_MCP_SERVERS``.
"""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import Any

_configs_cache: dict[str, dict[str, Any]] | None = None
_state_cache: dict[str, Any] | None = None


def _config_home() -> Path:
    return Path(os.getenv("DEEPCODE_CONFIG_HOME") or Path.home() / ".deepcode").resolve()


def _state_path() -> Path:
    return _config_home() / "config.json"


def _read_state() -> dict[str, Any]:
    global _state_cache
    if _state_cache is not None:
        return dict(_state_cache)
    try:
        data = json.loads(_state_path().read_text(encoding="utf-8"))
        _state_cache = data if isinstance(data, dict) else {}
    except Exception:
        _state_cache = {}
    return dict(_state_cache)


def _write_state(state: dict[str, Any]) -> None:
    global _state_cache
    _state_cache = dict(state)
    _state_path().parent.mkdir(parents=True, exist_ok=True)
    _state_path().write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def _is_env_falsy(value: str | None) -> bool:
    return str(value or "").strip().lower() in {"0", "false", "no", "off"}


def _normalize_name_for_mcp(value: str) -> str:
    normalized = re.sub(r"[^a-zA-Z0-9_]", "_", value.strip())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "managed_mcp"


def _load_servers_from_env() -> list[dict[str, Any]]:
    raw = os.getenv("DEEPCODE_CLAUDEAI_MCP_SERVERS") or os.getenv("DEEPSEEK_MANAGED_MCP_SERVERS")
    if not raw:
        return []
    try:
        parsed = json.loads(raw)
    except Exception:
        return []
    if isinstance(parsed, dict):
        if isinstance(parsed.get("data"), list):
            return [item for item in parsed["data"] if isinstance(item, dict)]
        return [dict({"display_name": name}, **server) for name, server in parsed.items() if isinstance(server, dict)]
    if isinstance(parsed, list):
        return [item for item in parsed if isinstance(item, dict)]
    return []


async def fetchClaudeAIMcpConfigsIfEligible() -> dict[str, dict[str, Any]]:
    global _configs_cache
    if _configs_cache is not None:
        return dict(_configs_cache)
    if _is_env_falsy(os.getenv("ENABLE_CLAUDEAI_MCP_SERVERS")):
        _configs_cache = {}
        return {}

    configs: dict[str, dict[str, Any]] = {}
    used_normalized: set[str] = set()
    for server in _load_servers_from_env():
        display_name = str(server.get("display_name") or server.get("name") or server.get("id") or "Managed")
        base_name = f"claude.ai {display_name}"
        final_name = base_name
        final_normalized = _normalize_name_for_mcp(final_name)
        count = 1
        while final_normalized in used_normalized:
            count += 1
            final_name = f"{base_name} ({count})"
            final_normalized = _normalize_name_for_mcp(final_name)
        used_normalized.add(final_normalized)
        if not server.get("url"):
            continue
        configs[final_name] = {
            "type": "claudeai-proxy",
            "url": str(server["url"]),
            "id": str(server.get("id") or final_normalized),
            "scope": "claudeai",
        }
    _configs_cache = configs
    return dict(configs)


def clearClaudeAIMcpConfigsCache() -> None:
    global _configs_cache
    _configs_cache = None


def markClaudeAiMcpConnected(name: str) -> None:
    state = _read_state()
    seen = list(state.get("claudeAiMcpEverConnected") or [])
    if name not in seen:
        seen.append(name)
        state["claudeAiMcpEverConnected"] = seen
        _write_state(state)


def hasClaudeAiMcpEverConnected(name: str) -> bool:
    return name in (_read_state().get("claudeAiMcpEverConnected") or [])


__all__ = [
    "clearClaudeAIMcpConfigsCache",
    "fetchClaudeAIMcpConfigsIfEligible",
    "hasClaudeAiMcpEverConnected",
    "markClaudeAiMcpConnected",
]
