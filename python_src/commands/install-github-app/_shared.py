"""Shared helpers for the DeepSeek GitHub app setup shim."""

from __future__ import annotations

import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any


GITHUB_APP_URL = os.environ.get("DEEPSEEK_GITHUB_APP_URL", "https://github.com/marketplace")
DEFAULT_SECRET_NAME = "DEEPSEEK_API_KEY"
DEFAULT_WORKFLOWS = ["deepseek", "deepseek-review"]


def normalize_repo(value: str | None = None) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    match = re.search(r"github\.com[:/]([^/]+/[^/.]+)(?:\.git)?/?$", raw)
    if match:
        return match.group(1)
    return raw.removesuffix(".git")


def detect_current_repo(cwd: str | None = None) -> str:
    root = Path(cwd or Path.cwd())
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    return normalize_repo(result.stdout.strip())


def check_gh_status() -> dict[str, Any]:
    if shutil.which("gh") is None:
        return {
            "ok": False,
            "warnings": [
                {
                    "title": "GitHub CLI not found",
                    "instructions": ["Install GitHub CLI from https://cli.github.com/", "Run `gh auth login`."],
                }
            ],
        }
    try:
        result = subprocess.run(["gh", "auth", "status", "-a"], capture_output=True, text=True, timeout=8, check=False)
    except Exception as exc:
        return {"ok": False, "warnings": [{"title": "GitHub CLI check failed", "message": str(exc)}]}
    if result.returncode != 0:
        return {
            "ok": False,
            "warnings": [
                {
                    "title": "GitHub CLI not authenticated",
                    "instructions": ["Run `gh auth login`.", "Refresh scopes with `gh auth refresh -h github.com -s repo,workflow`."],
                }
            ],
        }
    scopes = result.stdout + result.stderr
    missing = [scope for scope in ("repo", "workflow") if scope not in scopes]
    return {"ok": not missing, "warnings": [{"title": "Missing GitHub scopes", "missing": missing}] if missing else []}


def workflow_plan(
    repoName: str,
    secretName: str = DEFAULT_SECRET_NAME,
    selectedWorkflows: list[str] | None = None,
    skipWorkflow: bool = False,
    authType: str = "api_key",
) -> dict[str, Any]:
    workflows = selectedWorkflows or list(DEFAULT_WORKFLOWS)
    files = [] if skipWorkflow else [
        {
            "path": ".github/workflows/deepseek.yml",
            "description": "DeepSeek PR assistant workflow",
            "secretName": secretName,
        }
        for name in workflows
        if name in {"deepseek", "claude"}
    ] + [
        {
            "path": ".github/workflows/deepseek-code-review.yml",
            "description": "DeepSeek code review workflow",
            "secretName": secretName,
        }
        for name in workflows
        if name in {"deepseek-review", "claude-review"}
    ]
    return {
        "provider": "deepseek",
        "repo": normalize_repo(repoName),
        "secretName": secretName,
        "authType": authType,
        "skipWorkflow": skipWorkflow,
        "selectedWorkflows": workflows,
        "files": files,
        "commands": [
            "gh auth refresh -h github.com -s repo,workflow",
            f"gh secret set {secretName} --repo {normalize_repo(repoName) or '<owner/repo>'}",
        ],
        "manualUrl": GITHUB_APP_URL,
    }


def step_payload(step: str, **extra: Any) -> dict[str, Any]:
    return {"type": "github_app_step", "provider": "deepseek", "step": step, **extra}


__all__ = [
    "DEFAULT_SECRET_NAME",
    "DEFAULT_WORKFLOWS",
    "GITHUB_APP_URL",
    "check_gh_status",
    "detect_current_repo",
    "normalize_repo",
    "step_payload",
    "workflow_plan",
]
