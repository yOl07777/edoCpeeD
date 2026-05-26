"""Dry-run DeepSeek GitHub Actions setup planner."""

from __future__ import annotations

from typing import Any, Callable

from python_src.utils.config import saveGlobalConfig

from ._shared import DEFAULT_SECRET_NAME, DEFAULT_WORKFLOWS, workflow_plan


async def setupGitHubActions(
    repoName: str,
    apiKeyOrOAuthToken: str | None = None,
    secretName: str = DEFAULT_SECRET_NAME,
    updateProgress: Callable[[], Any] | None = None,
    skipWorkflow: bool = False,
    selectedWorkflows: list[str] | None = None,
    authType: str = "api_key",
    context: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if updateProgress:
        updateProgress()
    plan = workflow_plan(
        repoName=repoName,
        secretName=secretName,
        selectedWorkflows=selectedWorkflows or list(DEFAULT_WORKFLOWS),
        skipWorkflow=skipWorkflow,
        authType=authType,
    )
    plan["hasSecretValue"] = bool(apiKeyOrOAuthToken)
    plan["context"] = context or {}
    plan["dryRun"] = True
    plan["message"] = "Dry-run only: review and apply these GitHub Actions steps manually."
    await saveGlobalConfig(
        lambda current: {
            **current,
            "githubActionSetupCount": int(current.get("githubActionSetupCount") or 0) + 1,
            "lastGithubActionSetupProvider": "deepseek",
        }
    )
    if updateProgress:
        updateProgress()
    return plan


__all__ = ["setupGitHubActions"]
