from __future__ import annotations

from typing import Any

from python_src.tools.agent_store import answer_question, create_question
from python_src.tools.base import PythonTool, object_schema


async def ask_user_question(
    action: str,
    *,
    question: str | None = None,
    choices: list[str] | None = None,
    question_id: str | None = None,
    answer: str | None = None,
) -> dict[str, Any]:
    if action == "ask":
        if not question:
            raise ValueError("question is required for ask")
        return create_question(question, choices).to_dict()
    if action == "answer":
        if not question_id or answer is None:
            raise ValueError("question_id and answer are required for answer")
        return answer_question(question_id, answer).to_dict()
    raise ValueError(f"Unknown question action: {action}")


_sdkInputSchema = object_schema(
    {
        "action": {"type": "string", "enum": ["ask", "answer"]},
        "question": {"type": "string"},
        "choices": {"type": "array", "items": {"type": "string"}},
        "question_id": {"type": "string"},
        "answer": {"type": "string"},
    },
    required=["action"],
)
_sdkOutputSchema = {"type": "object"}

AskUserQuestionTool = PythonTool(
    name="ask_user_question",
    description="Record a question for the user or answer a recorded question.",
    parameters=_sdkInputSchema,
    handler=ask_user_question,
    read_only=False,
)
