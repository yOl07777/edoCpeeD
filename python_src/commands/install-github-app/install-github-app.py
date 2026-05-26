"""Local command shim for `/install-github-app`."""

from __future__ import annotations

from typing import Any, Callable

from ._shared import DEFAULT_SECRET_NAME, check_gh_status, detect_current_repo, normalize_repo, workflow_plan


def _parse_args(args: str | None, context: dict[str, Any] | None = None) -> str:
    raw = (args or "").strip()
    if raw:
        return normalize_repo(raw.split()[0])
    return detect_current_repo((context or {}).get("cwd"))


async def call(
    onDone: Callable[[str], Any] | None = None,
    context: dict[str, Any] | None = None,
    args: str = "",
) -> dict[str, Any]:
    repo = _parse_args(args, context)
    gh_status = check_gh_status()
    plan = workflow_plan(repo, DEFAULT_SECRET_NAME)
    value = (
        "Generated DeepSeek GitHub Actions setup guidance. "
        "No branch, secret, workflow, browser, or pull request was modified."
    )
    if onDone:
        onDone(value)
    return {
        "type": "github_app_setup",
        "provider": "deepseek",
        "value": value,
        "repo": repo,
        "gh": gh_status,
        "plan": plan,
        "args": args or "",
        "context": context or {},
    }


__all__ = ["call"]
