"""Structured creation-progress step."""

from __future__ import annotations

from typing import Any

from ._shared import step_payload


async def CreatingStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    current = int(kwargs.get("currentWorkflowInstallStep") or 0)
    return step_payload(
        "creating",
        currentWorkflowInstallStep=current,
        message="Dry-run only: no branch, workflow, secret, or pull request is created by this shim.",
    )


__all__ = ["CreatingStep"]
