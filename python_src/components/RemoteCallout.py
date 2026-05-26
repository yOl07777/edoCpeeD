from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option


async def RemoteCallout(*args: Any, **kwargs: Any) -> Any:
    return component_payload("remote_callout", visible=await shouldShowRemoteCallout(*args, **kwargs), environment=str(option(args, kwargs, "environment", "local")), text="Remote execution is available as a dry-run handoff.")


async def shouldShowRemoteCallout(*args: Any, **kwargs: Any) -> Any:
    return bool(option(args, kwargs, "remoteAvailable", option(args, kwargs, "remote_available", False))) and not bool(option(args, kwargs, "dismissed", False))


__all__ = ["RemoteCallout", "shouldShowRemoteCallout"]
