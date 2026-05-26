from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def useSwarmBanner(*args: Any, **kwargs: Any) -> Any:
    agents = kwargs.get("agents") or (args[0] if args else []) or []
    return prompt_payload("swarm_banner", active=bool(agents), agents=[str(agent) for agent in agents], count=len(agents))


__all__ = ["useSwarmBanner"]
