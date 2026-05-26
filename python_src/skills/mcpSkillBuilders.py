"""Write-once MCP skill builder registry."""

from __future__ import annotations

from typing import Any

_builders: dict[str, Any] | None = None


async def registerMCPSkillBuilders(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _builders
    builders = kwargs.get("builders") or (args[0] if args and isinstance(args[0], dict) else kwargs)
    _builders = dict(builders)
    return dict(_builders)


async def getMCPSkillBuilders(*args: Any, **kwargs: Any) -> dict[str, Any]:
    global _builders
    if _builders is None:
        from .loadSkillsDir import createSkillCommand, parseSkillFrontmatterFields

        _builders = {
            "createSkillCommand": createSkillCommand,
            "parseSkillFrontmatterFields": parseSkillFrontmatterFields,
        }
    return dict(_builders)


__all__ = ["getMCPSkillBuilders", "registerMCPSkillBuilders"]
