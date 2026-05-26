from __future__ import annotations

from typing import Any

from python_src.components.permissions.AskUserQuestionPermissionRequest._shared import question_state


async def QuestionNavigationBar(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = question_state(*args, **kwargs)
    index = state["index"]
    total = state["total"]
    return {
        "type": "question_navigation_bar",
        "provider": "deepseek",
        "index": index,
        "total": total,
        "canGoBack": index > 0,
        "canGoNext": index + 1 < total,
    }


__all__ = ["QuestionNavigationBar"]
