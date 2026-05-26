from __future__ import annotations

from typing import Any

from python_src.components.LogoV2._shared import logo_payload, notice_text, option, scalar_arg


async def EmergencyTip(*args: Any, **kwargs: Any) -> Any:
    text = notice_text(args, kwargs, str(scalar_arg(args, "Use /help, /status, or /exit if the terminal feels stuck.")))
    return logo_payload("emergency_tip", text=text, severity=str(option(args, kwargs, "severity", "info")))


__all__ = ["EmergencyTip"]
