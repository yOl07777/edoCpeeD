"""Initialize bundled DeepSeek Code skills."""

from __future__ import annotations

from typing import Any

from ..bundledSkills import clearBundledSkills, getBundledSkills
from .batch import registerBatchSkill
from .claudeApi import registerClaudeApiSkill
from .claudeInChrome import registerClaudeInChromeSkill
from .debug import registerDebugSkill
from .keybindings import registerKeybindingsSkill
from .loop import registerLoopSkill
from .loremIpsum import registerLoremIpsumSkill
from .remember import registerRememberSkill
from .scheduleRemoteAgents import registerScheduleRemoteAgentsSkill
from .simplify import registerSimplifySkill
from .skillify import registerSkillifySkill
from .stuck import registerStuckSkill
from .updateConfig import registerUpdateConfigSkill
from .verify import registerVerifySkill

_initialized = False


async def initBundledSkills(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    global _initialized
    if kwargs.get("reset"):
        await clearBundledSkills()
        _initialized = False
    if not _initialized:
        await registerBatchSkill()
        await registerClaudeApiSkill()
        await registerClaudeInChromeSkill()
        await registerDebugSkill()
        await registerKeybindingsSkill()
        await registerLoopSkill()
        await registerLoremIpsumSkill()
        await registerRememberSkill()
        await registerScheduleRemoteAgentsSkill()
        await registerSimplifySkill()
        await registerSkillifySkill()
        await registerStuckSkill()
        await registerUpdateConfigSkill()
        await registerVerifySkill()
        _initialized = True
    return await getBundledSkills()


__all__ = ["initBundledSkills"]
