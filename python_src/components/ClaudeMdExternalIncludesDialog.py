from __future__ import annotations

from typing import Any

from python_src.components._shared import component_payload, normalize_items, option


async def ClaudeMdExternalIncludesDialog(*args: Any, **kwargs: Any) -> Any:
    includes = normalize_items(option(args, kwargs, "includes", option(args, kwargs, "paths", [])), text_key="path")
    return component_payload(
        "external_includes_dialog",
        legacyName="ClaudeMdExternalIncludesDialog",
        includes=includes,
        count=len(includes),
        settingsPath=".deepseek/settings.json",
    )


__all__ = ["ClaudeMdExternalIncludesDialog"]
