from __future__ import annotations

from typing import Any

from python_src.components.HelpV2._shared import DEFAULT_COMMANDS, help_payload


async def Commands(*args: Any, **kwargs: Any) -> Any:
    commands = kwargs.get("commands") or (args[0] if args else None) or DEFAULT_COMMANDS
    query = str(kwargs.get("query") or "").lower()
    rows = []
    for command in commands:
        if isinstance(command, dict):
            name = str(command.get("name") or command.get("id") or "")
            description = str(command.get("description") or "")
        else:
            name = str(command)
            description = ""
        if not query or query in name.lower() or query in description.lower():
            rows.append({"name": name, "description": description})
    return help_payload("help_commands", commands=rows, count=len(rows), query=query)


__all__ = ["Commands"]
