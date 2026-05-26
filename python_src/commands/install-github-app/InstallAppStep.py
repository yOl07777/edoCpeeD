"""Structured GitHub app install step."""

from __future__ import annotations

from typing import Any

from ._shared import GITHUB_APP_URL, step_payload


async def InstallAppStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return step_payload(
        "install-app",
        url=GITHUB_APP_URL,
        message=f"Open the GitHub marketplace manually if your organization provides a DeepSeek GitHub App: {GITHUB_APP_URL}",
    )


__all__ = ["InstallAppStep"]
