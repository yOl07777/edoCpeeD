from __future__ import annotations

from typing import Any

from python_src.components.FeedbackSurvey._shared import survey_payload, timestamp


async def submitTranscriptShare(*args: Any, **kwargs: Any) -> Any:
    consent = bool(kwargs.get("consent", args[0] if args else False))
    transcript = kwargs.get("transcript") or ""
    return survey_payload(
        "transcript_share_submission",
        accepted=consent,
        uploaded=False,
        bytes=len(str(transcript).encode("utf-8")) if consent else 0,
        createdAt=timestamp(),
        message="Transcript share recorded locally; no network upload was performed.",
    )


__all__ = ["submitTranscriptShare"]
