from __future__ import annotations

from typing import Any

from python_src.components.permissions.AskUserQuestionPermissionRequest._shared import question_state


async def SubmitQuestionsView(*args: Any, **kwargs: Any) -> dict[str, Any]:
    state = question_state(*args, **kwargs)
    answers = kwargs.get("answers") or {}
    return {
        "type": "submit_questions_view",
        "provider": "deepseek",
        "questions": state["questions"],
        "answers": answers,
        "ready": len(answers) >= state["total"] if isinstance(answers, dict) else bool(answers),
    }


__all__ = ["SubmitQuestionsView"]
