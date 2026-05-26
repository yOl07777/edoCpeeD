from __future__ import annotations

import re
from typing import Any

from ._basic import first_mapping, pick


def _parts(version: str) -> tuple[int, int, int]:
    match = re.search(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?", version or "")
    if not match:
        return (0, 0, 0)
    return tuple(int(match.group(i) or 0) for i in range(1, 4))


async def getSemverPart(*args: Any, **kwargs: Any) -> Any:
    version = str(args[0] if args else kwargs.get("version", ""))
    part = str(args[1] if len(args) > 1 else kwargs.get("part", "major"))
    index = {"major": 0, "minor": 1, "patch": 2}.get(part, 0)
    return _parts(version)[index]

async def shouldShowUpdateNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    current = str(pick(options, "current", "currentVersion", default=args[0] if args and not isinstance(args[0], dict) else ""))
    latest = str(pick(options, "latest", "latestVersion", default=args[1] if len(args) > 1 else ""))
    dismissed = str(pick(options, "dismissedVersion", default=""))
    return _parts(latest) > _parts(current) and latest != dismissed

async def useUpdateNotification(*args: Any, **kwargs: Any) -> Any:
    options = first_mapping(*args, kwargs)
    current = str(pick(options, "current", "currentVersion", default="0.0.0"))
    latest = str(pick(options, "latest", "latestVersion", default=current))
    visible = await shouldShowUpdateNotification(current=current, latest=latest, dismissedVersion=pick(options, "dismissedVersion", default=""))
    return {"provider": "deepseek", "visible": visible, "currentVersion": current, "latestVersion": latest}
