from __future__ import annotations

from typing import Any

from python_src.components.permissions.AskUserQuestionPermissionRequest._shared import normalize_questions


async def useMultipleChoiceState(*args: Any, **kwargs: Any) -> dict[str, Any]:
    questions = normalize_questions(*args, **kwargs)
    selected = kwargs.get("selected") or {}
    return {
        "type": "multiple_choice_state",
        "provider": "deepseek",
        "questions": questions,
        "selected": selected,
        "complete": len(selected) >= len(questions) if isinstance(selected, dict) else bool(selected),
    }


__all__ = ["useMultipleChoiceState"]
