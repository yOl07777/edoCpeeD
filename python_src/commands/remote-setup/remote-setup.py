"""Runtime shim for `/web-setup`.

The original command rendered an Ink/React flow and imported local GitHub
credentials into Claude's web backend.  This Python migration keeps the command
callable and safe: it checks local prerequisites and returns actionable
DeepSeek-oriented status instead of performing remote token upload.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from typing import Any, Callable

try:  # pragma: no cover - importlib path loading fallback
    from .api import RedactedGithubToken, getCodeWebUrl, importGithubToken, isSignedIn
except ImportError:  # pragma: no cover
    import importlib.util
    from pathlib import Path

    _api_path = Path(__file__).with_name("api.py")
    _spec = importlib.util.spec_from_file_location("remote_setup_api", _api_path)
    if _spec is None or _spec.loader is None:
        raise
    _api = importlib.util.module_from_spec(_spec)
    sys.modules[_spec.name] = _api
    _spec.loader.exec_module(_api)
    RedactedGithubToken = _api.RedactedGithubToken
    getCodeWebUrl = _api.getCodeWebUrl
    importGithubToken = _api.importGithubToken
    isSignedIn = _api.isSignedIn


def errorMessage(err: dict[str, Any], codeUrl: str) -> str:
    kind = err.get("kind")
    if kind == "not_signed_in":
        return "未检测到 DeepSeek 凭据。请设置 DEEPSEEK_API_KEY 或 DEEPSEEK_API_KEYS。"
    if kind == "invalid_token":
        return "GitHub token 为空或无效。请运行 `gh auth login` 后重试。"
    if kind == "unsupported":
        return f"当前迁移版不会上传 GitHub token。请在网页端手动连接 GitHub：{codeUrl}"
    if kind == "server":
        return f"远端服务错误 ({err.get('status', 'unknown')})。稍后再试。"
    return "无法连接到远端服务。请检查网络连接。"


async def checkLoginState() -> dict[str, Any]:
    if not await isSignedIn():
        return {"status": "not_signed_in"}
    if shutil.which("gh") is None:
        return {"status": "gh_not_installed"}

    result = subprocess.run(
        ["gh", "auth", "token"],
        capture_output=True,
        text=True,
        timeout=5,
        check=False,
    )
    token = result.stdout.strip()
    if result.returncode != 0 or not token:
        return {"status": "gh_not_authenticated"}
    return {"status": "has_gh_token", "token": RedactedGithubToken(token)}


async def call(
    onDone: Callable[[str | None], Any] | None = None,
    context: dict[str, Any] | None = None,
    args: str = "",
) -> dict[str, Any]:
    code_url = getCodeWebUrl()
    state = await checkLoginState()
    status = state["status"]

    if status == "not_signed_in":
        message = "Not signed in to DeepSeek Code. Set DEEPSEEK_API_KEY first."
    elif status == "gh_not_installed":
        message = (
            "GitHub CLI not found. Install it via https://cli.github.com/, "
            f"then run `gh auth login`, or connect GitHub on the web: {code_url}"
        )
    elif status == "gh_not_authenticated":
        message = f"GitHub CLI not authenticated. Run `gh auth login`, or connect GitHub on the web: {code_url}"
    else:
        result = await importGithubToken(state["token"])
        if result["ok"]:
            message = f"Connected as {result['result']['github_username']}. Open {code_url}"
        else:
            message = errorMessage(result["error"], code_url)

    payload = {
        "type": "remote_setup",
        "provider": "deepseek",
        "status": status,
        "url": code_url,
        "args": args or "",
        "context": context or {},
        "value": message,
    }
    if onDone:
        onDone(message)
    return payload


__all__ = ["call", "checkLoginState", "errorMessage"]
