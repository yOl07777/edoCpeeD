"""Prompt command for creating DeepSeek verifier skills."""

from __future__ import annotations

from typing import Any


VERIFY_PROMPT = """Use the TodoWrite tool to track progress through this multi-step task.

## Goal

Create one or more verifier skills that the Verify agent can use to automatically verify functional behavior in this project or folder.

Do NOT create verifiers for normal unit tests or typechecking unless the project has a non-obvious wrapper around them. Focus on functional verification:
- Web UI verification with Playwright or browser MCP tools
- CLI verification with terminal sessions
- API verification with HTTP requests

## Phase 1: Auto-detection

Analyze the project for distinct areas:
- Top-level and subdirectory manifests: package.json, pyproject.toml, Cargo.toml, go.mod, pom.xml, etc.
- Application types: web app, CLI, API service, background worker, library
- Existing test and E2E tools
- Dev server commands, URLs, and readiness signals
- Existing .deepseek/skills, .claude/skills, .mcp.json, and browser automation configuration

## Phase 2: Choose verification tools

For web apps:
- If browser automation already exists, ask which option to use.
- If none exists, ask whether to set up Playwright, Chrome DevTools MCP, another browser MCP, or skip browser automation.
- If installation is needed, ask before running package-manager commands.

For CLI tools:
- Detect the command entry point and whether a persistent terminal/tmux-style session is useful.
- Keep setup lightweight and avoid recording tools unless the user wants them.

For API services:
- Detect curl/httpie availability and base URL.
- Ask about authentication only if routes appear protected or the user says so.

## Phase 3: Ask targeted questions

For each verifier, confirm:
- Verifier name. Folder name must include "verifier" so the Verify agent can discover it.
- Project area and command to start required services.
- URL, command, or endpoint to verify.
- Authentication method and secret env vars if needed. Never hardcode credentials.

## Phase 4: Generate skills

Create each skill at .deepseek/skills/<verifier-name>/SKILL.md. If this repo already standardizes on .claude/skills, preserve compatibility by reading existing skills first and explain where the new verifier was created.

Skill template:

```markdown
---
name: <verifier-name>
description: <when to use this verifier>
allowed-tools:
  - Bash(...)
  - Read
  - Glob
  - Grep
---

# <Verifier Title>

You are a verification executor. You receive a verification plan and execute it exactly as written.

## Project Context
<Project-specific details>

## Setup
<How to start any required services>

## Authentication
<Only include if auth is needed. Use environment variables for secrets.>

## Reporting
Report PASS or FAIL for each step using the format specified in the verification plan.

## Cleanup
Stop services or browser sessions started by this verifier.

## Self-update
If the verifier fails because its own instructions are outdated, ask before editing this SKILL.md with a minimal targeted fix.
```

## Phase 5: Confirm

Tell the user where each verifier skill was created, how it will be discovered, and how to customize it later.
"""


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    prompt = VERIFY_PROMPT
    if args and args.strip():
        prompt += f"\n\n## Additional user instructions\n\n{args.strip()}"
    return [{"type": "text", "text": prompt}]


initVerifiers = {
    "type": "prompt",
    "name": "init-verifiers",
    "description": "Create verifier skill(s) for automated verification of code changes",
    "contentLength": 0,
    "progressMessage": "analyzing your project and creating verifier skills",
    "source": "builtin",
    "getPromptForCommand": getPromptForCommand,
}

default = initVerifiers
