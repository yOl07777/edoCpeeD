from __future__ import annotations

from typing import Any

from python_src.components.PromptInput._shared import prompt_payload


async def IssueFlagBanner(*args: Any, **kwargs: Any) -> Any:
    issue = kwargs.get("issue") or (args[0] if args else None)
    return prompt_payload("issue_flag_banner", issue=issue, visible=bool(issue), message=f"Issue: {issue}" if issue else "")


__all__ = ["IssueFlagBanner"]
