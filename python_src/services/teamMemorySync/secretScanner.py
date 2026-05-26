"""High-confidence secret scanner for local team memory sync."""

from __future__ import annotations

import re
from typing import Any

_RULES: list[tuple[str, re.Pattern[str]]] = [
    ("aws-access-token", re.compile(r"\b((?:AKIA|ASIA|ABIA|ACCA)[A-Z0-9]{16})\b")),
    ("github-pat", re.compile(r"ghp_[0-9a-zA-Z]{36}")),
    ("github-fine-grained-pat", re.compile(r"github_pat_\w{82}")),
    ("gitlab-pat", re.compile(r"glpat-[\w-]{20}")),
    ("slack-bot-token", re.compile(r"xoxb-[0-9]{10,13}-[0-9]{10,13}[a-zA-Z0-9-]*")),
    ("openai-api-key", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
    ("anthropic-api-key", re.compile(r"sk-ant-(?:api|admin)[A-Za-z0-9_-]{20,}")),
    ("private-key", re.compile(r"-----BEGIN[ A-Z0-9_-]{0,100}PRIVATE KEY(?: BLOCK)?-----[\s\S-]{64,}?-----END[ A-Z0-9_-]{0,100}PRIVATE KEY(?: BLOCK)?-----", re.I)),
]


async def getSecretLabel(*args: Any, **kwargs: Any) -> str:
    rule_id = str(kwargs.get("ruleId") or kwargs.get("id") or (args[0] if args else "secret"))
    return " ".join(part.capitalize() for part in rule_id.replace("_", "-").split("-"))


async def scanForSecrets(*args: Any, **kwargs: Any) -> list[dict[str, str]]:
    content = str(kwargs.get("content") if "content" in kwargs else (args[0] if args else ""))
    matches: list[dict[str, str]] = []
    seen: set[str] = set()
    for rule_id, pattern in _RULES:
        if pattern.search(content) and rule_id not in seen:
            seen.add(rule_id)
            matches.append({"ruleId": rule_id, "label": await getSecretLabel(rule_id)})
    return matches


async def redactSecrets(*args: Any, **kwargs: Any) -> str:
    content = str(kwargs.get("content") if "content" in kwargs else (args[0] if args else ""))
    redacted = content
    for rule_id, pattern in _RULES:
        redacted = pattern.sub(f"[REDACTED:{rule_id}]", redacted)
    return redacted


__all__ = ["getSecretLabel", "redactSecrets", "scanForSecrets"]
