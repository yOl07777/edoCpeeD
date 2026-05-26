from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def PressEnterToContinue(*args: Any, **kwargs: Any) -> Any:
    message = str(option(args, kwargs, "message", scalar_arg(args, "Press Enter to continue")))
    return component_payload("press_enter_to_continue", message=message, key="enter", waiting=bool(option(args, kwargs, "waiting", True)))


__all__ = ["PressEnterToContinue"]
