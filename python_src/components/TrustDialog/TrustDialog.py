from __future__ import annotations

from typing import Any

from python_src.components.TrustDialog.utils import (
    getApiKeyHelperSources,
    getBashPermissionSources,
    getDangerousEnvVarsSources,
    getHooksSources,
)


async def TrustDialog(*args: Any, **kwargs: Any) -> Any:
    project = str(kwargs.get("project") or (args[0] if args else "workspace"))
    sources = [
        await getApiKeyHelperSources(kwargs.get("apiKeySources")),
        await getBashPermissionSources(kwargs.get("shellSources", [])),
        await getDangerousEnvVarsSources(kwargs.get("envSources", [])),
        await getHooksSources(kwargs.get("hookSources", [])),
    ]
    risks = [source for source in sources if source["count"] > 0]
    return {
        "type": "trust_dialog",
        "provider": "deepseek",
        "project": project,
        "trusted": bool(kwargs.get("trusted", False)),
        "risks": risks,
        "actions": ["trust", "cancel", "inspect"],
    }


__all__ = ["TrustDialog"]
