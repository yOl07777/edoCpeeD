from __future__ import annotations

from typing import Any

from python_src.components.shell._shared import shell_payload


async def ExpandShellOutputProvider(*args: Any, **kwargs: Any) -> Any:
    expanded = bool(kwargs.get("expanded", args[0] if args else False))
    return shell_payload("expand_shell_output_provider", expanded=expanded, children=kwargs.get("children"))


async def useExpandShellOutput(*args: Any, **kwargs: Any) -> Any:
    expanded = bool(kwargs.get("expanded", args[0] if args else False))
    return {"provider": "deepseek", "expanded": expanded, "toggle": not expanded}


__all__ = ["ExpandShellOutputProvider", "useExpandShellOutput"]
