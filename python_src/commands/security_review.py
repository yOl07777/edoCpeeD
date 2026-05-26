"""Security review prompt command."""

from __future__ import annotations

from typing import Any

from python_src.commands.createMovedToPluginCommand import createMovedToPluginCommand

SECURITY_REVIEW_MARKDOWN = """You are a senior security engineer conducting a focused security review of the changes on this branch.

GIT STATUS:

```bash
!`git status`
```

FILES MODIFIED:

```bash
!`git diff --name-only origin/HEAD...`
```

COMMITS:

```bash
!`git log --no-decorate origin/HEAD...`
```

DIFF CONTENT:

```bash
!`git diff origin/HEAD...`
```

OBJECTIVE:
Perform a security-focused code review to identify HIGH-CONFIDENCE security vulnerabilities that could have real exploitation potential. This is not a general code review; focus only on security implications newly added by this PR.

CRITICAL INSTRUCTIONS:
1. MINIMIZE FALSE POSITIVES: Only flag issues where you are more than 80% confident of actual exploitability.
2. AVOID NOISE: Skip theoretical issues, style concerns, and low-impact findings.
3. FOCUS ON IMPACT: Prioritize vulnerabilities that could lead to unauthorized access, data breaches, or system compromise.
4. EXCLUSIONS: Do not report DOS/resource exhaustion, secrets stored on disk, rate limiting concerns, documentation-only issues, or test-only issues.

SECURITY CATEGORIES TO EXAMINE:
- Input validation vulnerabilities such as SQL injection, command injection, XXE, template injection, NoSQL injection, and path traversal.
- Authentication and authorization bypasses, privilege escalation, session flaws, JWT issues, and authorization logic gaps.
- Crypto and secrets management issues such as hardcoded credentials, weak cryptography, improper key storage, or randomness problems.
- Injection and code execution issues such as unsafe deserialization, pickle/YAML loading, eval injection, and unsafe HTML rendering.
- Data exposure such as sensitive logging, PII mishandling, API leakage, and debug information exposure.

REQUIRED OUTPUT FORMAT:
Output markdown only. Each finding must include file, line number, severity, category, description, exploit scenario, confidence score, and fix recommendation.

Only include HIGH and MEDIUM findings with confidence 8/10 or higher."""


async def _fallbackPrompt(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    suffix = f"\n\nAdditional user instructions:\n{args.strip()}" if args and args.strip() else ""
    return [{"type": "text", "text": SECURITY_REVIEW_MARKDOWN + suffix}]


securityReview = createMovedToPluginCommand(
    name="security-review",
    description="Complete a security review of the pending changes on the current branch",
    progressMessage="analyzing code changes for security risks",
    pluginName="security-review",
    pluginCommand="security-review",
    getPromptWhileMarketplaceIsPrivate=_fallbackPrompt,
)

default = securityReview
