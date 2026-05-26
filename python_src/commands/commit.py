"""Prompt command for creating a safe git commit."""

from __future__ import annotations

from typing import Any

ALLOWED_TOOLS = ["Bash(git add:*)", "Bash(git status:*)", "Bash(git commit:*)"]


def getPromptContent() -> str:
    return """## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -10`

## Git Safety Protocol

- NEVER update the git config
- NEVER skip hooks (--no-verify, --no-gpg-sign, etc) unless the user explicitly requests it
- CRITICAL: ALWAYS create NEW commits. NEVER use git commit --amend, unless the user explicitly requests it
- Do not commit files that likely contain secrets (.env, credentials.json, etc). Warn the user if they specifically request to commit those files
- If there are no changes to commit, do not create an empty commit
- Never use git commands with the -i flag since they require interactive input which is not supported

## Your task

Based on the above changes, create a single git commit:

1. Analyze all staged and unstaged changes and draft a concise commit message.
2. Stage relevant files.
3. Create the commit using heredoc syntax:

```bash
git commit -m "$(cat <<'EOF'
Commit message here.
EOF
)"
```

Use only git status, git add, and git commit commands needed for this task."""


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    suffix = f"\n\n## Additional instructions from user\n\n{args.strip()}" if args and args.strip() else ""
    return [{"type": "text", "text": getPromptContent() + suffix}]


commit = {
    "type": "prompt",
    "name": "commit",
    "description": "Create a git commit",
    "allowedTools": ALLOWED_TOOLS,
    "contentLength": 0,
    "progressMessage": "creating commit",
    "source": "builtin",
    "getPromptForCommand": getPromptForCommand,
}

default = commit
