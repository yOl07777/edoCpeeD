"""Prompt constants for AskUserQuestionTool."""

from __future__ import annotations

ASK_USER_QUESTION_TOOL_NAME = "ask_user_question"
ASK_USER_QUESTION_TOOL_CHIP_WIDTH = 28
DESCRIPTION = "Record a question for the user or answer a recorded question."
ASK_USER_QUESTION_TOOL_PROMPT = (
    "Use this when progress genuinely depends on user input. Provide a concise question "
    "and, when possible, two or three concrete choices."
)
PREVIEW_FEATURE_PROMPT = "This local migration stores questions in process memory for testable dry-run flows."

__all__ = [
    "ASK_USER_QUESTION_TOOL_CHIP_WIDTH",
    "ASK_USER_QUESTION_TOOL_NAME",
    "ASK_USER_QUESTION_TOOL_PROMPT",
    "DESCRIPTION",
    "PREVIEW_FEATURE_PROMPT",
]
