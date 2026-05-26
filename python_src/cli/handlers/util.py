"""Miscellaneous CLI handlers."""

from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path
from typing import Any


async def setupTokenHandler(root: Any = None) -> dict[str, Any]:
    keys = [part.strip() for part in os.getenv("DEEPSEEK_API_KEYS", "").split(",") if part.strip()]
    return {
        "provider": "deepseek",
        "hasEnvApiKey": bool(os.getenv("DEEPSEEK_API_KEY") or keys),
        "keyCount": len(keys) or (1 if os.getenv("DEEPSEEK_API_KEY") else 0),
    }


async def doctorHandler(root: Any = None) -> dict[str, Any]:
    checks = {
        "python": sys.version.split()[0],
        "cwd": str(Path.cwd()),
        "deepseek_api_key": bool(os.getenv("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEYS")),
        "git": shutil.which("git") is not None,
    }
    return {"ok": all(value for key, value in checks.items() if key != "deepseek_api_key"), "checks": checks}


async def installHandler(target: str | None = None, local: bool = False, **kwargs: Any) -> dict[str, Any]:
    destination = Path(target or (Path.cwd() / ".deepcode"))
    if local:
        destination = Path.cwd() / destination
    destination.mkdir(parents=True, exist_ok=True)
    marker = destination / "installed.txt"
    marker.write_text("DeepCode Python migration local install marker\n", encoding="utf-8")
    return {"installed": True, "path": str(destination), "marker": str(marker)}
