from __future__ import annotations

from typing import Any

from python_src.commands.plugin.plugin import local_call


async def PluginSettings(*args: Any, **kwargs: Any) -> dict[str, Any]:
    on_complete = kwargs.get("onComplete")
    command_args = kwargs.get("args") or (args[0] if args and isinstance(args[0], str) else "")
    return await local_call(on_complete, kwargs.get("context"), command_args)


__all__ = ["PluginSettings"]
