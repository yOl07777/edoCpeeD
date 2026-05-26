from __future__ import annotations

from typing import Any

from python_src.components.HelpV2._shared import help_payload
from python_src.components.HelpV2.Commands import Commands
from python_src.components.HelpV2.General import General


async def HelpV2(*args: Any, **kwargs: Any) -> Any:
    tab = str(kwargs.get("tab") or (args[0] if args else "general"))
    return help_payload(
        "help_v2",
        tab=tab,
        general=await General(cwd=kwargs.get("cwd", "")),
        commands=await Commands(kwargs.get("commands"), query=kwargs.get("query", "")),
        tabs=["general", "commands"],
    )


__all__ = ["HelpV2"]
