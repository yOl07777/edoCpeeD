from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


FRAMES = ("|", "/", "-", "\\")


async def BriefIdleStatus(*args: Any, **kwargs: Any) -> Any:
    return component_payload("brief_idle_status", text=str(option(args, kwargs, "text", scalar_arg(args, "idle"))), idle=True)


async def Spinner(*args: Any, **kwargs: Any) -> Any:
    frame = int(option(args, kwargs, "frame", 0) or 0)
    return component_payload("spinner", frame=frame, glyph=FRAMES[frame % len(FRAMES)], text=str(option(args, kwargs, "text", "")))


async def SpinnerWithVerb(*args: Any, **kwargs: Any) -> Any:
    verb = str(option(args, kwargs, "verb", scalar_arg(args, "Working")))
    spinner = await Spinner(**kwargs)
    spinner["type"] = "spinner_with_verb"
    spinner["verb"] = verb
    spinner["text"] = f"{verb} {spinner['glyph']}"
    return spinner


__all__ = ["BriefIdleStatus", "Spinner", "SpinnerWithVerb"]
