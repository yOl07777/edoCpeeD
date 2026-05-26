"""Structured existing-workflow step."""

from __future__ import annotations

from typing import Any

from ._shared import step_payload


async def ExistingWorkflowStep(*args: Any, **kwargs: Any) -> dict[str, Any]:
    return step_payload(
        "check-existing-workflow",
        workflowExists=bool(kwargs.get("workflowExists", True)),
        message="Review existing workflow files manually before replacing or adding DeepSeek workflows.",
    )


__all__ = ["ExistingWorkflowStep"]
