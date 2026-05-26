from __future__ import annotations

import re
from urllib.parse import urlencode
from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


async def Feedback(*args: Any, **kwargs: Any) -> Any:
    body = await redactSensitiveInfo(option(args, kwargs, "body", scalar_arg(args, "")))
    title = str(option(args, kwargs, "title", "DeepSeek Code feedback"))
    return component_payload("feedback", title=title, body=body, issueUrl=await createGitHubIssueUrl(title=title, body=body))


async def createGitHubIssueUrl(*args: Any, **kwargs: Any) -> Any:
    repo = str(option(args, kwargs, "repo", "deepseek-code/deepseek-code"))
    title = str(option(args, kwargs, "title", scalar_arg(args, "Feedback")))
    body = str(option(args, kwargs, "body", ""))
    return f"https://github.com/{repo}/issues/new?{urlencode({'title': title, 'body': body})}"


async def redactSensitiveInfo(*args: Any, **kwargs: Any) -> Any:
    text = str(option(args, kwargs, "text", scalar_arg(args, "")))
    text = re.sub(r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*\S+", r"\1=***", text)
    text = re.sub(r"sk-[A-Za-z0-9_-]{8,}", "sk-***", text)
    return text


__all__ = ["Feedback", "createGitHubIssueUrl", "redactSensitiveInfo"]
