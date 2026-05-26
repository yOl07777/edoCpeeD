from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import logo_payload, normalize_feed_items, option, scalar_arg


def _feed_config(name: str, items: Any) -> dict[str, Any]:
    rows = normalize_feed_items(items)
    return logo_payload("feed_config", name=name, items=rows, count=len(rows))


async def createGuestPassesFeed(*args: Any, **kwargs: Any) -> Any:
    remaining = option(args, kwargs, "remaining", option(args, kwargs, "passes", scalar_arg(args, 0)))
    return _feed_config(
        "guest_passes",
        [
            {"text": f"Guest passes available: {remaining}", "tone": "success"},
            "Invite teammates from /team when ready",
        ],
    )


async def createProjectOnboardingFeed(*args: Any, **kwargs: Any) -> Any:
    project = str(option(args, kwargs, "project", option(args, kwargs, "cwd", scalar_arg(args, "this workspace"))))
    return _feed_config(
        "project_onboarding",
        [
            {"text": f"Project loaded: {project}", "tone": "info"},
            "Use /init to create local DeepSeek guidance",
            "Use /read and /write for terminal file workflows",
        ],
    )


async def createRecentActivityFeed(*args: Any, **kwargs: Any) -> Any:
    items = option(args, kwargs, "items", option(args, kwargs, "activity", scalar_arg(args)))
    return _feed_config("recent_activity", items or ["No recent activity yet", "Start by asking DeepSeek Code a task"])


async def createWhatsNewFeed(*args: Any, **kwargs: Any) -> Any:
    version = str(option(args, kwargs, "version", scalar_arg(args, "python-migration")))
    return _feed_config(
        "whats_new",
        [
            {"text": f"DeepSeek Code {version}", "tone": "success"},
            "Default model output streams in the terminal",
            "Local file tools can write after command approval",
        ],
    )


__all__ = [
    "createGuestPassesFeed",
    "createProjectOnboardingFeed",
    "createRecentActivityFeed",
    "createWhatsNewFeed",
]
