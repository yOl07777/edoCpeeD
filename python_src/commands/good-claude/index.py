"""Compatibility shim for the old good-claude command."""

from __future__ import annotations

from typing import Any


def buildGoodDeepSeekPrompt(args: str = "") -> str:
    focus = args.strip() or "the current task"
    return f"""Give feedback on how to make DeepSeek Code more effective for {focus}.

Focus on actionable guidance:
- What context is missing?
- Which instructions should be made more explicit?
- Which verification step would most reduce risk?
- What should be avoided because it would be speculative or too broad?

Return concise markdown bullets. Do not edit files."""


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    return [{"type": "text", "text": buildGoodDeepSeekPrompt(args)}]


good_deepseek = {
    "type": "prompt",
    "name": "good-deepseek",
    "aliases": ["good-claude"],
    "description": "Suggest how to make a DeepSeek Code task more effective",
    "progressMessage": "preparing DeepSeek effectiveness prompt",
    "allowedTools": [],
    "source": "builtin",
    "isHidden": True,
    "getPromptForCommand": getPromptForCommand,
}

default = good_deepseek
