"""Local DeepSeek mobile handoff command."""

from __future__ import annotations

from typing import Any, Callable

PLATFORMS = {
    "ios": {"url": "https://chat.deepseek.com", "label": "DeepSeek Chat on mobile web"},
    "android": {"url": "https://chat.deepseek.com", "label": "DeepSeek Chat on mobile web"},
}


def getMobileLinks() -> dict[str, dict[str, str]]:
    return {name: dict(info) for name, info in PLATFORMS.items()}


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    platform = args.strip().lower() if args and args.strip() else "ios"
    if platform not in PLATFORMS:
        platform = "ios"
    info = PLATFORMS[platform]
    value = f"Open {info['label']}: {info['url']}"
    if onDone:
        onDone(value)
    return {"type": "mobile_handoff", "platform": platform, "links": getMobileLinks(), "value": value}


mobile = {
    "type": "local",
    "name": "mobile",
    "aliases": ["ios", "android"],
    "description": "Show DeepSeek mobile handoff links",
    "source": "builtin",
    "supportsNonInteractive": True,
    "call": call,
}

default = mobile
