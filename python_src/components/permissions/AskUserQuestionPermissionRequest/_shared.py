from __future__ import annotations

from typing import Any


def normalize_questions(*args: Any, **kwargs: Any) -> list[dict[str, Any]]:
    raw = kwargs.get("questions") or kwargs.get("question") or (args[0] if args else [])
    if isinstance(raw, str):
        return [{"id": "question_1", "question": raw, "options": []}]
    if isinstance(raw, dict):
        raw = raw.get("questions") or [raw]
    questions: list[dict[str, Any]] = []
    for index, item in enumerate(raw or [], start=1):
        if isinstance(item, dict):
            question = dict(item)
        else:
            question = {"question": str(item)}
        question.setdefault("id", f"question_{index}")
        question.setdefault("options", [])
        questions.append(question)
    return questions


def question_state(*args: Any, **kwargs: Any) -> dict[str, Any]:
    questions = normalize_questions(*args, **kwargs)
    index = int(kwargs.get("index", 0) or 0)
    total = len(questions)
    current = questions[index] if 0 <= index < total else None
    return {
        "type": "ask_user_question_permission",
        "provider": "deepseek",
        "questions": questions,
        "index": index,
        "total": total,
        "current": current,
    }


__all__ = ["normalize_questions", "question_state"]
