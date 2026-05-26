"""Terminal spinner shims migrated for the DeepSeek Python runtime."""

from python_src.components.Spinner.index import *  # noqa: F401,F403
from python_src.components._shared import component_payload, option, scalar_arg


FRAMES = ("|", "/", "-", "\\")


async def BriefIdleStatus(*args, **kwargs):
    return component_payload("brief_idle_status", text=str(option(args, kwargs, "text", scalar_arg(args, "idle"))), idle=True)


async def Spinner(*args, **kwargs):
    frame = int(option(args, kwargs, "frame", 0) or 0)
    return component_payload("spinner", frame=frame, glyph=FRAMES[frame % len(FRAMES)], text=str(option(args, kwargs, "text", "")))


async def SpinnerWithVerb(*args, **kwargs):
    verb = str(option(args, kwargs, "verb", scalar_arg(args, "Working")))
    spinner = await Spinner(**kwargs)
    spinner["type"] = "spinner_with_verb"
    spinner["verb"] = verb
    spinner["text"] = f"{verb} {spinner['glyph']}"
    return spinner
