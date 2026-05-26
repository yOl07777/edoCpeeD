from __future__ import annotations

import shutil
import sys
from typing import Any

from deepseek_code.config import DeepSeekConfig
from python_src.commands.env.index import env_command
from python_src.tools import get_deepseek_tools


async def doctor_command() -> dict[str, Any]:
    config = DeepSeekConfig.from_env()
    checks = {
        "python": {"ok": True, "version": sys.version.split()[0]},
        "deepseek_api_keys": {"ok": bool(config.api_keys), "count": len(config.api_keys)},
        "deepseek_models": {"ok": bool(config.models), "models": config.models},
        "git": {"ok": shutil.which("git") is not None},
        "gh": {"ok": shutil.which("gh") is not None},
        "tools": {"ok": True, "count": len(get_deepseek_tools())},
    }
    ok = all(item.get("ok", False) for key, item in checks.items() if key not in {"gh", "deepseek_api_keys"})
    return {"ok": ok, "checks": checks, "env": await env_command()}


call = doctor_command
