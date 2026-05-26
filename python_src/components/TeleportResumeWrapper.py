from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, first_options, option, scalar_arg


async def TeleportResumeWrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
    data = dict(first_options(args))
    session = option(args, kwargs, "session", scalar_arg(args, data))
    if isinstance(session, dict):
        session_data = dict(session)
    else:
        session_data = {"id": str(session or "")}
    return component_payload("teleport_resume_wrapper", session=session_data, resumable=bool(option(args, kwargs, "resumable", bool(session_data.get("id")))))


__all__ = ["TeleportResumeWrapper"]
