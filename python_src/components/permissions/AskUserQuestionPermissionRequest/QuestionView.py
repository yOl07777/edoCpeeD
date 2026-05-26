from __future__ import annotations

from typing import Any

from python_src.components.permissions.AskUserQuestionPermissionRequest._shared import question_state


async def QuestionView(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = question_state(*args, **kwargs)
    state["type"] = "question_view"
    return state


__all__ = ["QuestionView"]
