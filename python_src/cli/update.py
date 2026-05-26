"""Local update-check shim for the Python DeepSeek migration."""

from __future__ import annotations

import importlib.metadata
import os
from typing import Any


def _version() -> str:
    try:
        return importlib.metadata.version("deepseek-code")
    except importlib.metadata.PackageNotFoundError:
        return os.getenv("DEEPCODE_VERSION", "0.0.0")


async def update(options: dict[str, Any] | None = None, **kwargs: Any) -> dict[str, Any]:
    opts = {**(options or {}), **kwargs}
    current = _version()
    channel = str(opts.get("channel") or os.getenv("DEEPCODE_UPDATE_CHANNEL") or "latest")
    latest = opts.get("latestVersion") or os.getenv("DEEPCODE_LATEST_VERSION")
    update_available = bool(latest and str(latest) != current)
    command = "pip install --upgrade deepseek-code"
    result = {
        "currentVersion": current,
        "channel": channel,
        "latestVersion": latest or current,
        "updateAvailable": update_available,
        "managedBy": "python",
        "command": command if update_available else None,
    }
    if not opts.get("quiet"):
        print(f"Current version: {current}")
        print(f"Checking for updates to {channel} version...")
        if update_available:
            print(f"Update available: {current} -> {latest}")
            print(f"To update, run: {command}")
        else:
            print("DeepSeek Code is up to date.")
    return result
