from __future__ import annotations

from typing import Any

from ._notification import first_mapping, pick


async def useInstallMessages(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    installed = pick(options, "installed", "packages", default=[]) or []
    failed = pick(options, "failed", "errors", default=[]) or []
    messages = []
    for name in installed:
        messages.append({"level": "success", "message": f"Installed {name}."})
    for name in failed:
        messages.append({"level": "error", "message": f"Failed to install {name}."})
    return {"provider": "deepseek", "visible": bool(messages), "messages": messages}
