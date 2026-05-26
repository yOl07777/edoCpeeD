from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option, scalar_arg


async def RemoteEnvironmentDialog(*args: Any, **kwargs: Any) -> Any:
    env = normalize_items(option(args, kwargs, "environment", option(args, kwargs, "env", scalar_arg(args, []))), text_key="name")
    return component_payload("remote_environment_dialog", environment=env, count=len(env), dryRun=True)


__all__ = ["RemoteEnvironmentDialog"]
