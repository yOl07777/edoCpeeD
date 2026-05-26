"""Shared helpers for migrated bundled skill registrations."""

from __future__ import annotations

from typing import Any

from ..bundledSkills import registerBundledSkill


async def register_simple_skill(name: str, description: str, **extra: Any) -> dict[str, Any]:
    async def prompt(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
        text = f"{description}\n\nUse this DeepSeek Code bundled skill to help with: {name}."
        if args:
            text += f"\n\nArguments: {args}"
        return [{"type": "text", "text": text}]

    return await registerBundledSkill(
        {
            "name": name,
            "description": description,
            "getPromptForCommand": prompt,
            **extra,
        }
    )


__all__ = ["register_simple_skill"]
