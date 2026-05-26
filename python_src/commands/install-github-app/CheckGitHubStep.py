"""Structured GitHub CLI prerequisite check."""

from __future__ import annotations

from typing import Any

from ._shared import check_gh_status, step_payload


async def CheckGitHubStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    status = check_gh_status()
    return step_payload("check-gh", ok=status["ok"], warnings=status["warnings"])


__all__ = ["CheckGitHubStep"]
