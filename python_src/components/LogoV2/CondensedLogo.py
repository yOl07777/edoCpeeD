from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import SHORT_LOGO_TEXT, logo_payload, option, scalar_arg


async def CondensedLogo(*args: Any, **kwargs: Any) -> Any:
    label = str(option(args, kwargs, "label", scalar_arg(args, SHORT_LOGO_TEXT)))
    return logo_payload("condensed_logo", text=label, width=len(label), compact=True)


__all__ = ["CondensedLogo"]
