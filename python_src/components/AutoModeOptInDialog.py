from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option


AUTO_MODE_DESCRIPTION = "Let DeepSeek Code continue low-risk local steps while preserving tool approval boundaries."


async def AutoModeOptInDialog(*args: Any, **kwargs: Any) -> Any:
    rules = normalize_items(option(args, kwargs, "rules", ["Ask before file writes", "Ask before shell commands", "Never expose API keys"]))
    return component_payload(
        "auto_mode_opt_in_dialog",
        description=AUTO_MODE_DESCRIPTION,
        accepted=bool(option(args, kwargs, "accepted", False)),
        rules=rules,
    )


__all__ = ["AUTO_MODE_DESCRIPTION", "AutoModeOptInDialog"]
