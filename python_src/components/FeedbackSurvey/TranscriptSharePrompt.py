from __future__ import annotations

from typing import Any

from python_src.components.FeedbackSurvey._shared import survey_payload


async def TranscriptSharePrompt(*args: Any, **kwargs: Any) -> Any:
    return survey_payload(
        "transcript_share_prompt",
        title="Share transcript",
        body="Allow DeepSeek Code to include this transcript in local feedback metadata.",
        defaultConsent=bool(kwargs.get("defaultConsent", False)),
        choices=["yes", "no"],
    )


__all__ = ["TranscriptSharePrompt"]
