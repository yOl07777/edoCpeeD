"""Facade for the `/review` prompt command plus review helpers."""

from __future__ import annotations

from typing import Any


def localReviewPrompt(args: str = "") -> str:
    pr_number = (args or "").strip()
    return f"""You are an expert code reviewer. Follow these steps:

1. If no PR number is provided in the args, run `gh pr list` to show open PRs.
2. If a PR number is provided, run `gh pr view <number>` to get PR details.
3. Run `gh pr diff <number>` to get the diff.
4. Analyze the changes and provide a thorough code review that includes:
   - Overview of what the PR does
   - Analysis of code quality and style
   - Specific suggestions for improvements
   - Any potential issues or risks

Keep your review concise but thorough. Focus on:
- Code correctness
- Following project conventions
- Performance implications
- Test coverage
- Security considerations

Format your review with clear sections and bullet points.

PR number: {pr_number}"""


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    return [{"type": "text", "text": localReviewPrompt(args)}]


review = {
    "type": "prompt",
    "name": "review",
    "description": "Review a pull request",
    "progressMessage": "reviewing pull request",
    "contentLength": 0,
    "source": "builtin",
    "getPromptForCommand": getPromptForCommand,
}

default = review

__all__ = ["default", "getPromptForCommand", "localReviewPrompt", "review"]
