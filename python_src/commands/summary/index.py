"""Prompt command for summarizing the current session."""

from __future__ import annotations

from typing import Any

from python_src.session_store import SESSION_STATE


def buildSummaryPrompt(args: str = "") -> str:
    transcript = SESSION_STATE.export_jsonl() or "(No in-memory session messages.)"
    focus = f"\n\nUser focus: {args.strip()}" if args and args.strip() else ""
    return (
        "Summarize the current DeepSeek Code session for future continuation.\n\n"
        "Include:\n"
        "- User goal\n"
        "- Decisions made\n"
        "- Files or modules touched if known\n"
        "- Remaining work and verification status\n\n"
        f"Session transcript JSONL:\n{transcript}{focus}"
    )


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    return [{"type": "text", "text": buildSummaryPrompt(args)}]


summary = {
    "type": "prompt",
    "name": "summary",
    "description": "Summarize the current session",
    "contentLength": 0,
    "progressMessage": "summarizing session",
    "source": "builtin",
    "getPromptForCommand": getPromptForCommand,
}

default = summary

__all__ = ["buildSummaryPrompt", "default", "getPromptForCommand", "summary"]
