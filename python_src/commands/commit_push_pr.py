"""Prompt command for committing, pushing, and opening a pull request."""

from __future__ import annotations

import os
from typing import Any

ALLOWED_TOOLS = [
    "Bash(git checkout --branch:*)",
    "Bash(git checkout -b:*)",
    "Bash(git add:*)",
    "Bash(git status:*)",
    "Bash(git push:*)",
    "Bash(git commit:*)",
    "Bash(gh pr create:*)",
    "Bash(gh pr edit:*)",
    "Bash(gh pr view:*)",
    "Bash(gh pr merge:*)",
    "ToolSearch",
    "mcp__slack__send_message",
    "mcp__deepseek_ai_Slack__slack_send_message",
]


def getPromptContent(defaultBranch: str = "main", prAttribution: str | None = None) -> str:
    safe_user = os.getenv("SAFEUSER", "")
    username = os.getenv("USER") or os.getenv("USERNAME") or ""
    attribution = f"\n\n{prAttribution}" if prAttribution else ""
    return f"""## Context

- `SAFEUSER`: {safe_user}
- `whoami`: {username}
- `git status`: !`git status`
- `git diff HEAD`: !`git diff HEAD`
- `git branch --show-current`: !`git branch --show-current`
- `git diff {defaultBranch}...HEAD`: !`git diff {defaultBranch}...HEAD`
- `gh pr view --json number 2>/dev/null || true`: !`gh pr view --json number 2>/dev/null || true`

## Git Safety Protocol

- NEVER update the git config
- NEVER run destructive or irreversible git commands unless the user explicitly requests them
- NEVER skip hooks (--no-verify, --no-gpg-sign, etc) unless the user explicitly requests it
- NEVER run force push to main/master; warn the user if they request it
- Do not commit files that likely contain secrets (.env, credentials.json, etc)
- Never use git commands with the -i flag since they require interactive input which is not supported

## Your task

Analyze all changes that will be included in the pull request. Look at all commits and the complete diff from `{defaultBranch}...HEAD`.

Based on the above changes:

1. Create a new branch if on `{defaultBranch}`. Use SAFEUSER as the branch prefix, falling back to whoami.
2. Create a single commit with an appropriate message using heredoc syntax:

```bash
git commit -m "$(cat <<'EOF'
Commit message here.
EOF
)"
```

3. Push the branch to origin.
4. If a PR already exists for this branch, update the PR title and body using `gh pr edit`. Otherwise create a PR using:

```bash
gh pr create --title "Short, descriptive title" --body "$(cat <<'EOF'
## Summary
- <1-3 bullets>

## Test plan
- [ ] <test performed or planned>

## Changelog
<!-- CHANGELOG:START -->
[If this PR contains user-facing changes, add a changelog entry here. Otherwise, remove this section.]
<!-- CHANGELOG:END -->{attribution}
EOF
)"
```

Return the PR URL when finished."""


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    default_branch = "main"
    if isinstance(context, dict):
        default_branch = str(context.get("defaultBranch") or context.get("default_branch") or default_branch)
    prompt = getPromptContent(default_branch)
    if args and args.strip():
        prompt += f"\n\n## Additional instructions from user\n\n{args.strip()}"
    return [{"type": "text", "text": prompt}]


commitPushPr = {
    "type": "prompt",
    "name": "commit-push-pr",
    "description": "Commit, push, and open a PR",
    "allowedTools": ALLOWED_TOOLS,
    "contentLength": 0,
    "progressMessage": "creating commit and PR",
    "source": "builtin",
    "getPromptForCommand": getPromptForCommand,
}

default = commitPushPr
