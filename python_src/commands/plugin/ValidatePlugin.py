from __future__ import annotations

from typing import Any

from python_src.cli.handlers.plugins import pluginValidateHandler
from python_src.commands.plugin._shared import command_result


async def ValidatePlugin(*args: Any, **kwargs: Any) -> dict[str, Any]:
    path = kwargs.get("path") or (args[0] if args else None)
    if not path:
        return command_result("Specify a plugin manifest path.")
    result = await pluginValidateHandler(str(path), kwargs)
    return command_result(
        "Plugin manifest is valid." if result.get("success") else "Plugin manifest has errors.",
        result=result,
    )


__all__ = ["ValidatePlugin"]
