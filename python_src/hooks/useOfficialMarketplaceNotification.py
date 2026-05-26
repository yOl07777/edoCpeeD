from __future__ import annotations

from typing import Any

from ._basic import first_mapping, normalize_bool, pick


async def useOfficialMarketplaceNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    source = str(pick(options, "source", "marketplace", default="local"))
    dismissed = normalize_bool(pick(options, "dismissed", default=False))
    official = normalize_bool(pick(options, "official", "isOfficial", default=source == "official"))
    visible = official and not dismissed
    return {
        "provider": "deepseek",
        "visible": visible,
        "source": source,
        "message": "This plugin comes from the official DeepSeek Code marketplace." if visible else "",
    }
