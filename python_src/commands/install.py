from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Callable


def getInstallPlan(cwd: str | None = None) -> dict[str, Any]:
    root = Path(cwd or os.getcwd())
    venv = root / ".venv"
    return {
        "provider": "deepseek",
        "cwd": str(root),
        "python": sys.executable,
        "venv": str(venv),
        "commands": [
            "python -m venv .venv",
            ".venv\\Scripts\\activate",
            "pip install -r requirements.txt",
            "python -m deepseek_code.cli",
        ],
        "env": [".env", "DEEPSEEK_API_KEYS", "DEFAULT_MODEL"],
    }


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    cwd = context.get("cwd") if isinstance(context, dict) else None
    plan = getInstallPlan(cwd)
    value = "DeepSeek Code install plan prepared. No install commands were executed."
    if args:
        plan["args"] = args
    if onDone:
        onDone(value)
    return {"type": "install", "value": value, "plan": plan}


install = {
    "type": "local",
    "name": "install",
    "description": "Show local DeepSeek Code installation steps",
    "supportsNonInteractive": True,
    "source": "builtin",
    "call": call,
}

default = install


__all__ = ["call", "default", "getInstallPlan", "install"]
