from __future__ import annotations

AGENT_PATHS = {
    "FOLDER_NAME": ".deepseek",
    "LEGACY_FOLDER_NAME": ".claude",
    "AGENTS_DIR": "agents",
}

ModeState = dict
AgentValidationResult = dict


__all__ = ["AGENT_PATHS", "AgentValidationResult", "ModeState"]
