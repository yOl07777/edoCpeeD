from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, option, scalar_arg


async def SessionPreview(*args: Any, **kwargs: Any) -> Any:
    session = option(args, kwargs, "session", scalar_arg(args, first_options(args)))
    title = str(session.get("title", session.get("id", "session")) if isinstance(session, dict) else session)
    return component_payload("session_preview", session=session, title=title, messageCount=session.get("messageCount", 0) if isinstance(session, dict) else 0)


__all__ = ["SessionPreview"]
