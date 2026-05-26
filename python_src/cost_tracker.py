"""Session cost tracking adapted for DeepSeek/OpenAI usage payloads."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

from python_src.bootstrap import state as bootstrap_state
from python_src.cost_store import COST_STATE
from python_src.utils.config import getCurrentProjectConfig, saveCurrentProjectConfig
from python_src.utils.modelCost import calculateUSDCost


def _usage_value(usage: Any, snake: str, camel: str | None = None, default: int | float = 0) -> int | float:
    if isinstance(usage, dict):
        if snake in usage:
            return usage.get(snake) or default
        if camel and camel in usage:
            return usage.get(camel) or default
    return getattr(usage, snake, getattr(usage, camel or snake, default)) or default


def _web_search_requests(usage: Any) -> int:
    server_tool_use = _usage_value(usage, "server_tool_use", "serverToolUse", {})
    if isinstance(server_tool_use, dict):
        return int(server_tool_use.get("web_search_requests") or server_tool_use.get("webSearchRequests") or 0)
    return int(getattr(server_tool_use, "web_search_requests", getattr(server_tool_use, "webSearchRequests", 0)) or 0)


def _current_cost_state() -> dict[str, Any]:
    return bootstrap_state.getStateSnapshot()


def formatCost(cost: int | float, maxDecimalPlaces: int = 4) -> str:
    value = float(cost or 0)
    if value > 0.5:
        return f"${round(value, 2):.2f}"
    return f"${value:.{maxDecimalPlaces}f}"


def _format_number(value: int | float) -> str:
    return f"{int(value):,}"


def _format_duration(ms: int | float | None) -> str:
    total_ms = int(ms or 0)
    seconds = total_ms // 1000
    if seconds < 60:
        return f"{seconds}s"
    minutes, seconds = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {seconds}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {seconds}s"


def _default_model_usage() -> dict[str, Any]:
    return {
        "inputTokens": 0,
        "outputTokens": 0,
        "cacheReadInputTokens": 0,
        "cacheCreationInputTokens": 0,
        "webSearchRequests": 0,
        "costUSD": 0.0,
        "contextWindow": 0,
        "maxOutputTokens": 0,
    }


def _canonical_model_name(model: str | None) -> str:
    text = (model or "deepseek-chat").strip()
    aliases = {
        "deepseek-v3": "deepseek-chat",
        "deepseek-v4": "deepseek-chat",
        "deepseek-coder": "deepseek-chat",
        "deepseek-r1": "deepseek-reasoner",
    }
    return aliases.get(text.lower(), text)


def _accumulate_model_usage(cost: float, usage: Any, model: str) -> dict[str, Any]:
    model_key = _canonical_model_name(model)
    model_usage = bootstrap_state.getModelUsage() or {}
    current = deepcopy(model_usage.get(model_key) or _default_model_usage())
    current["inputTokens"] = int(current.get("inputTokens", 0)) + int(_usage_value(usage, "input_tokens", "inputTokens"))
    current["outputTokens"] = int(current.get("outputTokens", 0)) + int(_usage_value(usage, "output_tokens", "outputTokens"))
    current["cacheReadInputTokens"] = int(current.get("cacheReadInputTokens", 0)) + int(
        _usage_value(usage, "cache_read_input_tokens", "cacheReadInputTokens")
    )
    current["cacheCreationInputTokens"] = int(current.get("cacheCreationInputTokens", 0)) + int(
        _usage_value(usage, "cache_creation_input_tokens", "cacheCreationInputTokens")
    )
    current["webSearchRequests"] = int(current.get("webSearchRequests", 0)) + _web_search_requests(usage)
    current["costUSD"] = float(current.get("costUSD", 0.0)) + float(cost or 0)
    model_usage[model_key] = current
    bootstrap_state.setCostStateForRestore({"modelUsage": model_usage})
    return deepcopy(current)


async def addToTotalSessionCost(cost: float | None, usage: Any, model: str) -> float:
    actual_cost = float(cost if cost is not None else await calculateUSDCost(model, usage))
    _accumulate_model_usage(actual_cost, usage, model)

    snapshot = _current_cost_state()
    input_tokens = int(_usage_value(usage, "input_tokens", "inputTokens"))
    output_tokens = int(_usage_value(usage, "output_tokens", "outputTokens"))
    cache_read = int(_usage_value(usage, "cache_read_input_tokens", "cacheReadInputTokens"))
    cache_creation = int(_usage_value(usage, "cache_creation_input_tokens", "cacheCreationInputTokens"))
    web_search = _web_search_requests(usage)

    bootstrap_state.setCostStateForRestore(
        {
            "totalCostUSD": float(snapshot.get("totalCostUSD", 0.0)) + actual_cost,
            "costCounter": float(snapshot.get("costCounter", 0.0)) + actual_cost,
            "totalInputTokens": int(snapshot.get("totalInputTokens", 0)) + input_tokens,
            "totalOutputTokens": int(snapshot.get("totalOutputTokens", 0)) + output_tokens,
            "totalCacheReadInputTokens": int(snapshot.get("totalCacheReadInputTokens", 0)) + cache_read,
            "totalCacheCreationInputTokens": int(snapshot.get("totalCacheCreationInputTokens", 0)) + cache_creation,
            "totalWebSearchRequests": int(snapshot.get("totalWebSearchRequests", 0)) + web_search,
        }
    )
    COST_STATE.add(input_tokens=input_tokens, output_tokens=output_tokens, total_usd=actual_cost)
    return actual_cost


def _format_model_usage() -> str:
    usage_by_model = bootstrap_state.getModelUsage() or {}
    if not usage_by_model:
        return "Usage:                 0 input, 0 output, 0 cache read, 0 cache write"

    lines = ["Usage by model:"]
    for model in sorted(usage_by_model):
        usage = usage_by_model[model]
        usage_string = (
            f"{_format_number(usage.get('inputTokens', 0))} input, "
            f"{_format_number(usage.get('outputTokens', 0))} output, "
            f"{_format_number(usage.get('cacheReadInputTokens', 0))} cache read, "
            f"{_format_number(usage.get('cacheCreationInputTokens', 0))} cache write"
        )
        if int(usage.get("webSearchRequests", 0)):
            usage_string += f", {_format_number(usage.get('webSearchRequests', 0))} web search"
        usage_string += f" ({formatCost(float(usage.get('costUSD', 0.0)))})"
        lines.append(f"{(model + ':').rjust(21)} {usage_string}")
    return "\n".join(lines)


async def formatTotalCost() -> str:
    snapshot = _current_cost_state()
    cost_display = formatCost(float(snapshot.get("totalCostUSD", 0.0)))
    if bootstrap_state.hasUnknownModelCost():
        cost_display += " (costs may be inaccurate due to usage of unknown models)"
    added = int(snapshot.get("totalLinesAdded", 0))
    removed = int(snapshot.get("totalLinesRemoved", 0))
    return (
        f"Total cost:            {cost_display}\n"
        f"Total duration (API):  {_format_duration(snapshot.get('totalAPIDuration'))}\n"
        f"Total duration (wall): {_format_duration(snapshot.get('totalDuration'))}\n"
        f"Total code changes:    {added} {'line' if added == 1 else 'lines'} added, "
        f"{removed} {'line' if removed == 1 else 'lines'} removed\n"
        f"{_format_model_usage()}"
    )


async def getStoredSessionCosts(sessionId: str) -> dict[str, Any] | None:
    project_config = await getCurrentProjectConfig()
    if project_config.get("lastSessionId") != sessionId:
        return None
    return {
        "totalCostUSD": float(project_config.get("lastCost") or 0.0),
        "totalAPIDuration": int(project_config.get("lastAPIDuration") or 0),
        "totalAPIDurationWithoutRetries": int(project_config.get("lastAPIDurationWithoutRetries") or 0),
        "totalToolDuration": int(project_config.get("lastToolDuration") or 0),
        "totalLinesAdded": int(project_config.get("lastLinesAdded") or 0),
        "totalLinesRemoved": int(project_config.get("lastLinesRemoved") or 0),
        "totalInputTokens": int(project_config.get("lastTotalInputTokens") or 0),
        "totalOutputTokens": int(project_config.get("lastTotalOutputTokens") or 0),
        "totalCacheCreationInputTokens": int(project_config.get("lastTotalCacheCreationInputTokens") or 0),
        "totalCacheReadInputTokens": int(project_config.get("lastTotalCacheReadInputTokens") or 0),
        "totalWebSearchRequests": int(project_config.get("lastTotalWebSearchRequests") or 0),
        "lastDuration": project_config.get("lastDuration"),
        "modelUsage": deepcopy(project_config.get("lastModelUsage") or {}),
    }


async def restoreCostStateForSession(sessionId: str) -> bool:
    stored = await getStoredSessionCosts(sessionId)
    if not stored:
        return False
    restore = dict(stored)
    restore["totalDuration"] = int(stored.get("lastDuration") or 0)
    restore.pop("lastDuration", None)
    bootstrap_state.setCostStateForRestore(restore)
    return True


async def saveCurrentSessionCosts(fpsMetrics: Any | None = None) -> dict[str, Any]:
    snapshot = _current_cost_state()
    model_usage = bootstrap_state.getModelUsage() or {}
    fps_average = _usage_value(fpsMetrics, "averageFps", "average_fps", None) if fpsMetrics is not None else None
    fps_low = _usage_value(fpsMetrics, "low1PctFps", "low_1pct_fps", None) if fpsMetrics is not None else None
    return await saveCurrentProjectConfig(
        {
            "lastCost": snapshot.get("totalCostUSD", 0.0),
            "lastAPIDuration": snapshot.get("totalAPIDuration", 0),
            "lastAPIDurationWithoutRetries": snapshot.get("totalAPIDurationWithoutRetries", 0),
            "lastToolDuration": snapshot.get("totalToolDuration", 0),
            "lastDuration": snapshot.get("totalDuration", 0),
            "lastLinesAdded": snapshot.get("totalLinesAdded", 0),
            "lastLinesRemoved": snapshot.get("totalLinesRemoved", 0),
            "lastTotalInputTokens": snapshot.get("totalInputTokens", 0),
            "lastTotalOutputTokens": snapshot.get("totalOutputTokens", 0),
            "lastTotalCacheCreationInputTokens": snapshot.get("totalCacheCreationInputTokens", 0),
            "lastTotalCacheReadInputTokens": snapshot.get("totalCacheReadInputTokens", 0),
            "lastTotalWebSearchRequests": snapshot.get("totalWebSearchRequests", 0),
            "lastFpsAverage": fps_average,
            "lastFpsLow1Pct": fps_low,
            "lastModelUsage": deepcopy(model_usage),
            "lastSessionId": bootstrap_state.getSessionId(),
        }
    )


getTotalCost = bootstrap_state.getTotalCostUSD
getTotalDuration = bootstrap_state.getTotalDuration
getTotalAPIDuration = bootstrap_state.getTotalAPIDuration
getTotalAPIDurationWithoutRetries = bootstrap_state.getTotalAPIDurationWithoutRetries
addToTotalLinesChanged = bootstrap_state.addToTotalLinesChanged
getTotalLinesAdded = bootstrap_state.getTotalLinesAdded
getTotalLinesRemoved = bootstrap_state.getTotalLinesRemoved
getTotalInputTokens = bootstrap_state.getTotalInputTokens
getTotalOutputTokens = bootstrap_state.getTotalOutputTokens
getTotalCacheReadInputTokens = bootstrap_state.getTotalCacheReadInputTokens
getTotalCacheCreationInputTokens = bootstrap_state.getTotalCacheCreationInputTokens
getTotalWebSearchRequests = bootstrap_state.getTotalWebSearchRequests
hasUnknownModelCost = bootstrap_state.hasUnknownModelCost
resetStateForTests = bootstrap_state.resetStateForTests
resetCostState = bootstrap_state.resetCostState
setHasUnknownModelCost = bootstrap_state.setHasUnknownModelCost
getModelUsage = bootstrap_state.getModelUsage
getUsageForModel = bootstrap_state.getUsageForModel
