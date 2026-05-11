from __future__ import annotations

import os
from typing import Any

from deepseek_code.config import DeepSeekConfig
from python_src.commands.branch.branch import call as branch_command
from python_src.utils.github.ghAuthStatus import getGhAuthStatus
from python_src.utils.settings.settings import getInitialSettings, getSettingsWithSources


async def status_command(cwd: str | os.PathLike[str] | None = None) -> dict[str, Any]:
    config = DeepSeekConfig.from_env()
    settings_with_sources = await getSettingsWithSources(cwd)
    settings = settings_with_sources["settings"]
    branch = await branch_command("current", cwd=cwd)
    gh = await getGhAuthStatus(str(cwd) if cwd else None)
    return {
        "provider": settings.get("provider", "deepseek"),
        "model": settings.get("model") or settings.get("defaultModel") or config.default_model,
        "endpoint_count": len(config.endpoints),
        "model_count": len(config.models),
        "api_key_count": len(config.api_keys),
        "settings_errors": settings_with_sources["errors"],
        "branch": branch,
        "github": {"available": gh["available"], "authenticated": gh["authenticated"]},
    }


call = status_command
