from __future__ import annotations

from typing import Any

from python_src.cli.handlers.plugins import marketplaceAddHandler
from python_src.commands.plugin._shared import command_result


async def AddMarketplace(*args: Any, **kwargs: Any) -> dict[str, Any]:
    source = kwargs.get("source") or (args[0] if args else None)
    if not source:
        return command_result("Specify a marketplace source to add.")
    result = await marketplaceAddHandler(str(source), kwargs)
    return command_result(f"Added marketplace: {source}", result=result)


__all__ = ["AddMarketplace"]
