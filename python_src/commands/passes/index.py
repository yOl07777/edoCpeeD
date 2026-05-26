"""Passes command metadata."""

from __future__ import annotations

import importlib


async def _description() -> str:
    from python_src.services.api.referral import getCachedReferrerReward

    reward = await getCachedReferrerReward()
    if reward:
        return "Share DeepSeek Code access with friends and track remaining passes"
    return "Share DeepSeek Code access with friends"


async def _is_hidden() -> bool:
    from python_src.services.api.referral import checkCachedPassesEligibility

    eligibility = await checkCachedPassesEligibility()
    return not bool(eligibility and eligibility.get("eligible"))


default = {
    "type": "local-jsx",
    "name": "passes",
    "description": _description,
    "isHidden": _is_hidden,
    "load": lambda: importlib.import_module("python_src.commands.passes.passes"),
}
