from __future__ import annotations

from typing import Any

from python_src.commands.plugin._shared import command_result


async def buildFinalValues(defaults: dict[str, Any] | None = None, values: dict[str, Any] | None = None, *args: Any, **kwargs: Any) -> dict[str, Any]:
    return {**(defaults or {}), **(values or {}), **kwargs.get("values", {})}


async def PluginOptionsDialog(*args: Any, **kwargs: Any) -> dict[str, Any]:
    final_values = await buildFinalValues(kwargs.get("defaults"), kwargs.get("values"))
    return command_result("Plugin options resolved.", values=final_values)


__all__ = ["PluginOptionsDialog", "buildFinalValues"]
