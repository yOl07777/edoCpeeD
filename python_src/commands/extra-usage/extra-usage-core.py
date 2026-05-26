"""Core logic for `/extra-usage` in the DeepSeek migration."""

from __future__ import annotations

import os
from typing import Any

from python_src.utils.config import getGlobalConfig, saveGlobalConfig


USAGE_URL = "https://platform.deepseek.com/usage"
BILLING_URL = "https://platform.deepseek.com/billing"


def _truthy(value: Any) -> bool:
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "on"}


async def runExtraUsage() -> dict[str, Any]:
    config = await getGlobalConfig()
    if not config.get("hasVisitedExtraUsage"):
        await saveGlobalConfig({"hasVisitedExtraUsage": True})

    limit_hit = _truthy(os.getenv("DEEPSEEK_RATE_LIMIT_HIT"))
    tier = os.getenv("DEEPSEEK_RATE_LIMIT_TIER", "standard")
    usage_url = os.getenv("DEEPSEEK_USAGE_URL", USAGE_URL)
    billing_url = os.getenv("DEEPSEEK_BILLING_URL", BILLING_URL)

    if os.getenv("DEEPSEEK_API_KEYS"):
        return {
            "type": "message",
            "value": (
                "Multiple DeepSeek API keys are configured. The load balancer can rotate to another key "
                "when one hits a retryable limit. Review current usage at "
                f"{usage_url} or billing limits at {billing_url}."
            ),
            "usageUrl": usage_url,
            "billingUrl": billing_url,
            "tier": tier,
            "limitHit": limit_hit,
        }

    return {
        "type": "browser-opened",
        "url": billing_url if limit_hit else usage_url,
        "opened": False,
        "usageUrl": usage_url,
        "billingUrl": billing_url,
        "tier": tier,
        "limitHit": limit_hit,
    }
