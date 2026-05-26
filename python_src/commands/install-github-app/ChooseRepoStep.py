"""Structured repository selection step."""

from __future__ import annotations

from typing import Any

from ._shared import detect_current_repo, normalize_repo, step_payload


async def ChooseRepoStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    context = kwargs.get("context") if isinstance(kwargs.get("context"), dict) else {}
    repo = normalize_repo(kwargs.get("selectedRepoName") or (args[0] if args else "") or detect_current_repo(context.get("cwd")))
    warnings = []
    if repo and "/" not in repo:
        warnings.append({"title": "Repository format warning", "message": 'Use "owner/repo".'})
    return step_payload("choose-repo", selectedRepoName=repo, useCurrentRepo=bool(repo), warnings=warnings)


__all__ = ["ChooseRepoStep"]
