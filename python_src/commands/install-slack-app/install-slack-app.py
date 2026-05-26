"""Local shim for `/install-slack-app`.

Claude Code opened Claude's Slack marketplace page.  The DeepSeek migration
keeps the command callable but avoids browser side effects; it records local
interest and returns the integration URL/instructions as structured text.
"""

from __future__ import annotations

import os
from typing import Any, Callable

from python_src.utils.config import saveGlobalConfig


SLACK_APP_URL = os.environ.get("DEEPSEEK_SLACK_APP_URL", "https://slack.com/marketplace")


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: dict[str, Any] | None = None,
    args: str = "",
) -> dict[str, Any]:
    config = await saveGlobalConfig(
        lambda current: {
            **current,
            "slackAppInstallCount": int(current.get("slackAppInstallCount") or 0) + 1,
            "lastSlackAppInstallProvider": "deepseek",
        }
    )
    value = (
        "DeepSeek Code does not auto-open or install a Slack app from this Python shim. "
        f"Visit the Slack marketplace manually if your workspace has a DeepSeek integration: {SLACK_APP_URL}"
    )
    if onDone:
        onDone(value)
    return {
        "type": "text",
        "provider": "deepseek",
        "value": value,
        "url": SLACK_APP_URL,
        "installCount": config.get("slackAppInstallCount", 0),
        "args": args or "",
        "context": context or {},
    }


__all__ = ["SLACK_APP_URL", "call"]
