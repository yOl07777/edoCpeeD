"""Implementation helpers for the DeepSeek Think Back shim."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from python_src.session_store import SESSION_STATE

EDIT_PROMPT = (
    'Use the Skill tool to invoke the "thinkback" skill with mode=edit to modify my existing '
    "DeepSeek Code year in review. Ask what should change, then summarize the update."
)
FIX_PROMPT = (
    'Use the Skill tool to invoke the "thinkback" skill with mode=fix to fix validation or rendering '
    "errors in my existing DeepSeek Code year in review."
)
REGENERATE_PROMPT = (
    'Use the Skill tool to invoke the "thinkback" skill with mode=regenerate to create a new '
    "DeepSeek Code year in review from the current local session history."
)


async def playAnimation(skillDir: str | None = None) -> dict[str, Any]:
    root = Path(skillDir or ".").resolve()
    html = root / "year_in_review.html"
    data = root / "year_in_review.js"
    if html.exists() or data.exists():
        return {
            "success": True,
            "message": f"Think Back assets are available in {root}. Open them manually to play.",
            "path": str(root),
        }
    return {
        "success": False,
        "message": "No Think Back animation found. Run /think-back to prepare one.",
        "path": str(root),
    }


def buildThinkbackPrompt(args: str = "") -> str:
    mode = (args.strip() or "regenerate").lower()
    if mode == "edit":
        return EDIT_PROMPT
    if mode == "fix":
        return FIX_PROMPT
    if mode == "play":
        return "Run /thinkback-play to inspect local Think Back animation assets."
    transcript = SESSION_STATE.export_jsonl()
    return (
        "Create a concise DeepSeek Code year-in-review from the current session. "
        "Highlight meaningful work completed, commands migrated, verification status, and next priorities. "
        "Do not install plugins or run remote marketplace commands.\n\n"
        f"## Session JSONL\n\n{transcript or '(no in-memory messages)'}"
    )


async def call(
    onDone: Callable[..., Any] | None = None,
    context: Any | None = None,
    args: str = "",
) -> dict[str, Any]:
    prompt = buildThinkbackPrompt(args)
    result = {"type": "thinkback", "value": prompt, "prompt": prompt, "shouldQuery": True}
    if onDone:
        try:
            onDone(prompt, {"display": "user", "shouldQuery": True})
        except TypeError:
            onDone(prompt)
    return result
