"""DeepSeek upgrade/account command shim."""

from __future__ import annotations

import os
from typing import Any, Callable

from python_src.utils.auth import getAccountInformation, getSubscriptionName, getSubscriptionType

UPGRADE_URL = "https://platform.deepseek.com"


def isEnabled() -> bool:
    return os.getenv("DISABLE_UPGRADE_COMMAND", "").lower() not in {"1", "true", "yes", "on"}


async def getUpgradeStatus() -> dict[str, Any]:
    return {
        "provider": "deepseek",
        "url": UPGRADE_URL,
        "account": await getAccountInformation(),
        "subscriptionType": await getSubscriptionType(),
        "subscriptionName": await getSubscriptionName(),
    }


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    status = await getUpgradeStatus()
    value = (
        "DeepSeek usage is managed through API keys, model choice, and provider billing. "
        f"Manage account or billing at: {UPGRADE_URL}"
    )
    if onDone:
        onDone(value)
    return {"type": "upgrade", "value": value, "status": status}


upgrade = {
    "type": "local",
    "name": "upgrade",
    "description": "Show DeepSeek account and billing management link",
    "source": "builtin",
    "supportsNonInteractive": True,
    "isEnabled": isEnabled,
    "call": call,
}

default = upgrade
