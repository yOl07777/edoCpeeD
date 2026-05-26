from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import logo_payload, notice_text, option


async def Opus1mMergeNotice(*args: Any, **kwargs: Any) -> Any:
    visible = await shouldShowOpus1mMergeNotice(*args, **kwargs)
    text = notice_text(args, kwargs, "DeepSeek long-context routing is handled by the selected model.")
    return logo_payload("long_context_merge_notice", visible=visible, text=text)


async def shouldShowOpus1mMergeNotice(*args: Any, **kwargs: Any) -> Any:
    model = str(option(args, kwargs, "model", ""))
    dismissed = bool(option(args, kwargs, "dismissed", False))
    return bool(option(args, kwargs, "enabled", True)) and not dismissed and ("reasoner" in model or "long" in model)


__all__ = ["Opus1mMergeNotice", "shouldShowOpus1mMergeNotice"]
