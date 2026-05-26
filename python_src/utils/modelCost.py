"""DeepSeek/OpenAI compatible token cost helpers."""

from __future__ import annotations

import os
from copy import deepcopy
from typing import Any

from python_src.bootstrap.state import setHasUnknownModelCost


ModelCosts = dict[str, float]

COST_DEEPSEEK_CHAT: ModelCosts = {
    "inputTokens": 0.14,
    "outputTokens": 0.28,
    "promptCacheWriteTokens": 0.14,
    "promptCacheReadTokens": 0.0028,
    "webSearchRequests": 0.0,
}

COST_DEEPSEEK_REASONER: ModelCosts = {
    "inputTokens": 0.14,
    "outputTokens": 0.28,
    "promptCacheWriteTokens": 0.14,
    "promptCacheReadTokens": 0.0028,
    "webSearchRequests": 0.0,
}

COST_DEEPSEEK_CODER: ModelCosts = deepcopy(COST_DEEPSEEK_CHAT)

COST_TIER_3_15 = {"inputTokens": 3.0, "outputTokens": 15.0, "promptCacheWriteTokens": 3.75, "promptCacheReadTokens": 0.3, "webSearchRequests": 0.01}
COST_TIER_15_75 = {"inputTokens": 15.0, "outputTokens": 75.0, "promptCacheWriteTokens": 18.75, "promptCacheReadTokens": 1.5, "webSearchRequests": 0.01}
COST_TIER_5_25 = {"inputTokens": 5.0, "outputTokens": 25.0, "promptCacheWriteTokens": 6.25, "promptCacheReadTokens": 0.5, "webSearchRequests": 0.01}
COST_TIER_30_150 = {"inputTokens": 30.0, "outputTokens": 150.0, "promptCacheWriteTokens": 37.5, "promptCacheReadTokens": 3.0, "webSearchRequests": 0.01}
COST_HAIKU_35 = {"inputTokens": 0.8, "outputTokens": 4.0, "promptCacheWriteTokens": 1.0, "promptCacheReadTokens": 0.08, "webSearchRequests": 0.01}
COST_HAIKU_45 = {"inputTokens": 1.0, "outputTokens": 5.0, "promptCacheWriteTokens": 1.25, "promptCacheReadTokens": 0.1, "webSearchRequests": 0.01}

MODEL_COSTS: dict[str, ModelCosts] = {
    "deepseek-chat": COST_DEEPSEEK_CHAT,
    "deepseek-v3": COST_DEEPSEEK_CHAT,
    "deepseek-v4": COST_DEEPSEEK_CHAT,
    "deepseek-v4-flash": COST_DEEPSEEK_CHAT,
    "deepseek-coder": COST_DEEPSEEK_CODER,
    "deepseek-reasoner": COST_DEEPSEEK_REASONER,
    "deepseek-r1": COST_DEEPSEEK_REASONER,
}

_ALIASES = {
    "chat": "deepseek-chat",
    "coder": "deepseek-coder",
    "reasoner": "deepseek-reasoner",
    "deepseek-v3.2-exp": "deepseek-chat",
}


def _canonical(model: str | None) -> str:
    text = (model or os.getenv("DEFAULT_MODEL") or "deepseek-chat").strip().lower()
    return _ALIASES.get(text, text)


def _env_price(model: str, field: str, fallback: float) -> float:
    env_model = model.upper().replace("-", "_").replace(".", "_")
    env_field = field.upper()
    for name in (
        f"DEEPSEEK_PRICE_{env_model}_{env_field}_PER_MTOK",
        f"DEEPSEEK_PRICE_{env_field}_PER_MTOK",
    ):
        value = os.getenv(name)
        if value:
            try:
                return float(value)
            except ValueError:
                pass
    return fallback


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


async def getOpus46CostTier(fastMode: bool = False) -> ModelCosts:
    return deepcopy(COST_TIER_30_150 if fastMode else COST_TIER_5_25)


async def getModelCosts(model: str, usage: Any | None = None) -> ModelCosts:
    canonical = _canonical(model)
    costs = deepcopy(MODEL_COSTS.get(canonical) or MODEL_COSTS["deepseek-chat"])
    if canonical not in MODEL_COSTS:
        setHasUnknownModelCost(True)
    return {
        "inputTokens": _env_price(canonical, "INPUT", costs["inputTokens"]),
        "outputTokens": _env_price(canonical, "OUTPUT", costs["outputTokens"]),
        "promptCacheWriteTokens": _env_price(canonical, "CACHE_WRITE", costs["promptCacheWriteTokens"]),
        "promptCacheReadTokens": _env_price(canonical, "CACHE_READ", costs["promptCacheReadTokens"]),
        "webSearchRequests": _env_price(canonical, "WEB_SEARCH", costs["webSearchRequests"]),
    }


async def calculateUSDCost(resolvedModel: str, usage: Any) -> float:
    costs = await getModelCosts(resolvedModel, usage)
    return (
        (float(_usage_value(usage, "input_tokens", "inputTokens")) / 1_000_000) * costs["inputTokens"]
        + (float(_usage_value(usage, "output_tokens", "outputTokens")) / 1_000_000) * costs["outputTokens"]
        + (float(_usage_value(usage, "cache_read_input_tokens", "cacheReadInputTokens")) / 1_000_000) * costs["promptCacheReadTokens"]
        + (float(_usage_value(usage, "cache_creation_input_tokens", "cacheCreationInputTokens")) / 1_000_000) * costs["promptCacheWriteTokens"]
        + _web_search_requests(usage) * costs["webSearchRequests"]
    )


async def calculateCostFromTokens(model: str, tokens: dict[str, int | float]) -> float:
    usage = {
        "input_tokens": tokens.get("inputTokens", tokens.get("input_tokens", 0)),
        "output_tokens": tokens.get("outputTokens", tokens.get("output_tokens", 0)),
        "cache_read_input_tokens": tokens.get("cacheReadInputTokens", tokens.get("cache_read_input_tokens", 0)),
        "cache_creation_input_tokens": tokens.get("cacheCreationInputTokens", tokens.get("cache_creation_input_tokens", 0)),
    }
    return await calculateUSDCost(model, usage)


def _format_price(price: float) -> str:
    return f"${int(price)}" if float(price).is_integer() else f"${price:.3f}".rstrip("0").rstrip(".")


async def formatModelPricing(costs: ModelCosts) -> str:
    return f"{_format_price(costs['inputTokens'])}/{_format_price(costs['outputTokens'])} per Mtok"


async def getModelPricingString(model: str) -> str | None:
    canonical = _canonical(model)
    if canonical not in MODEL_COSTS:
        return None
    return await formatModelPricing(await getModelCosts(canonical))


__all__ = [
    "COST_DEEPSEEK_CHAT",
    "COST_DEEPSEEK_CODER",
    "COST_DEEPSEEK_REASONER",
    "COST_HAIKU_35",
    "COST_HAIKU_45",
    "COST_TIER_15_75",
    "COST_TIER_30_150",
    "COST_TIER_3_15",
    "COST_TIER_5_25",
    "MODEL_COSTS",
    "calculateCostFromTokens",
    "calculateUSDCost",
    "formatModelPricing",
    "getModelCosts",
    "getModelPricingString",
    "getOpus46CostTier",
]
