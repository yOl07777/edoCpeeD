from __future__ import annotations

from typing import Any

from python_src.components.hooks._shared import MATCHER_MODES, hook_payload


async def SelectMatcherMode(*args: Any, **kwargs: Any) -> Any:
    selected = str(kwargs.get("matcherMode") or kwargs.get("mode") or (args[0] if args else "all"))
    matcher = str(kwargs.get("matcher") or "*")
    return hook_payload(
        "select_hook_matcher_mode",
        selected=selected,
        matcher=matcher,
        modes=[{"id": mode, "selected": mode == selected} for mode in MATCHER_MODES],
        valid=selected in MATCHER_MODES,
    )


__all__ = ["SelectMatcherMode"]
