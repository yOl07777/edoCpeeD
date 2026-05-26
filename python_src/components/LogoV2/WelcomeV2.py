from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import LOGO_TEXT, logo_payload, option, scalar_arg


async def WelcomeV2(*args: Any, **kwargs: Any) -> Any:
    cwd = str(option(args, kwargs, "cwd", option(args, kwargs, "project", scalar_arg(args, ""))))
    tips = option(
        args,
        kwargs,
        "tips",
        ["/help lists commands", "/status shows model and key state", "/write can create files after approval"],
    )
    return logo_payload("welcome_v2", title=LOGO_TEXT, cwd=cwd, tips=[str(tip) for tip in tips], ready=True)


__all__ = ["WelcomeV2"]
