from __future__ import annotations

from typing import Any

from ._common import register_simple_skill


async def registerKeybindingsSkill(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return await register_simple_skill("keybindings", "Help inspect and update keyboard shortcut configuration.", allowedTools=["Read", "Edit"])


__all__ = ["registerKeybindingsSkill"]
