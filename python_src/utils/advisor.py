"""Advisor feature helpers adapted for the DeepSeek Python runtime."""

from __future__ import annotations

import os
from typing import Any

from python_src.utils.model.aliases import resolve_model_alias


ADVISOR_TOOL_INSTRUCTIONS = """# Advisor Tool

You have access to an `advisor` tool backed by a stronger reviewer model. It
takes no parameters; when called, the current conversation can be forwarded by
the runtime. Call it before committing to a substantial approach, when stuck,
and before declaring larger tasks complete.
"""


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


def _advisor_config() -> dict[str, Any]:
    return {
        "enabled": _truthy(os.getenv("DEEPSEEK_ADVISOR_ENABLED")),
        "canUserConfigure": _truthy(os.getenv("DEEPSEEK_ADVISOR_CONFIGURABLE", "1")),
        "baseModel": os.getenv("DEEPSEEK_ADVISOR_BASE_MODEL"),
        "advisorModel": os.getenv("DEEPSEEK_ADVISOR_MODEL"),
    }


def isAdvisorBlock(param: dict[str, Any] | Any) -> bool:
    block_type = param.get("type") if isinstance(param, dict) else getattr(param, "type", None)
    name = param.get("name") if isinstance(param, dict) else getattr(param, "name", None)
    return block_type == "advisor_tool_result" or (block_type == "server_tool_use" and name == "advisor")


def isAdvisorEnabled() -> bool:
    if _truthy(os.getenv("CLAUDE_CODE_DISABLE_ADVISOR_TOOL")) or _truthy(os.getenv("DEEPSEEK_DISABLE_ADVISOR_TOOL")):
        return False
    return bool(_advisor_config().get("enabled") or os.getenv("USER_TYPE") == "ant")


def canUserConfigureAdvisor() -> bool:
    config = _advisor_config()
    return isAdvisorEnabled() and bool(config.get("canUserConfigure", False))


def getExperimentAdvisorModels() -> dict[str, str] | None:
    config = _advisor_config()
    base_model = config.get("baseModel")
    advisor_model = config.get("advisorModel")
    if isAdvisorEnabled() and not canUserConfigureAdvisor() and base_model and advisor_model:
        return {"baseModel": str(base_model), "advisorModel": str(advisor_model)}
    return None


def modelSupportsAdvisor(model: str | None) -> bool:
    canonical = resolve_model_alias(model).lower()
    return os.getenv("USER_TYPE") == "ant" or canonical in {"deepseek-reasoner", "deepseek-coder"} or "reasoner" in canonical


def isValidAdvisorModel(model: str | None) -> bool:
    canonical = resolve_model_alias(model).lower()
    return os.getenv("USER_TYPE") == "ant" or canonical.startswith("deepseek-")


def getInitialAdvisorSetting(settings: dict[str, Any] | None = None) -> str | None:
    if not isAdvisorEnabled():
        return None
    configured = _advisor_config().get("advisorModel")
    if configured:
        return str(configured)
    if settings:
        value = settings.get("advisorModel")
        return str(value) if value else None
    return None


def getAdvisorUsage(usage: dict[str, Any] | Any) -> list[dict[str, Any]]:
    iterations = usage.get("iterations") if isinstance(usage, dict) else getattr(usage, "iterations", None)
    if not isinstance(iterations, list):
        return []
    return [item for item in iterations if isinstance(item, dict) and item.get("type") == "advisor_message"]
