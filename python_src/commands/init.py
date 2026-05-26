"""Prompt command for initializing DeepSeek Code repository instructions."""

from __future__ import annotations

import os
from typing import Any

from python_src.projectOnboardingState import maybeMarkProjectOnboardingComplete


OLD_INIT_PROMPT = """Please analyze this codebase and create a DEEPSEEK.md file, which will be given to future instances of DeepSeek Code to operate in this repository.

What to add:
1. Commands that will be commonly used, such as how to build, lint, and run tests. Include the necessary commands to develop in this codebase, such as how to run a single test.
2. High-level code architecture and structure so future DeepSeek Code sessions can be productive more quickly. Focus on the big-picture architecture that requires reading multiple files to understand.

Usage notes:
- If there's already a DEEPSEEK.md, suggest improvements to it.
- If there is an existing CLAUDE.md, AGENTS.md, .cursor/rules, .cursorrules, .github/copilot-instructions.md, .windsurfrules, or .clinerules file, read it and migrate only the important repository-specific guidance.
- Do not repeat yourself and do not include obvious generic instructions.
- Avoid listing every component or file structure that can be easily discovered.
- Do not include generic development practices.
- If there is a README.md, include only the important parts that DeepSeek Code would otherwise miss.
- Do not make up information such as "Common Development Tasks" or "Support and Documentation" unless this is expressly included in other files that you read.
- Be sure to prefix the file with:

```
# DEEPSEEK.md

This file provides guidance to DeepSeek Code when working with code in this repository.
```
"""


NEW_INIT_PROMPT = """Set up minimal DeepSeek Code repository guidance files for this repo. DEEPSEEK.md is loaded into future DeepSeek Code sessions, so keep it concise: only include what the model would get wrong without it.

## Phase 1: Ask what to set up

Use AskUserQuestion to find out what the user wants:

- "Which guidance files should /init set up?"
  Options: "Project DEEPSEEK.md" | "Personal DEEPSEEK.local.md" | "Both project + personal"
  Description for project: "Team-shared instructions checked into source control: architecture, coding standards, common workflows."
  Description for personal: "Private preferences for this project (gitignored, not shared): role, sandbox URLs, preferred test data, workflow quirks."

- "Also set up skills and hooks?"
  Options: "Skills + hooks" | "Skills only" | "Hooks only" | "Neither, just guidance files"
  Description for skills: "On-demand capabilities invoked with /skill-name for repeatable workflows and reference knowledge."
  Description for hooks: "Deterministic shell commands that run on tool events, such as format after every edit."

## Phase 2: Explore the codebase

Launch a subagent to survey the codebase. Read key files: manifest files, README, Makefile/build configs, CI config, existing DEEPSEEK.md, CLAUDE.md, AGENTS.md, .deepseek/rules, .claude/rules, .cursor/rules, .cursorrules, .github/copilot-instructions.md, .windsurfrules, .clinerules, and .mcp.json.

Detect:
- Build, test, and lint commands, especially non-standard ones
- Languages, frameworks, package manager, and project layout
- Code style rules that differ from language defaults
- Required environment variables, workflow quirks, or gotchas
- Existing .deepseek/skills, .claude/skills, .deepseek/rules, and .claude/rules directories
- Formatter configuration and fast verification commands
- Git worktree usage if personal guidance files are requested

Note what cannot be inferred from code alone; those become interview questions.

## Phase 3: Fill in gaps

Ask only questions the code cannot answer. Synthesize a compact proposal for:
- Project guidance notes
- Personal guidance notes
- Skills for repeatable workflows
- Hooks for mechanical, fast checks

Respect the user's Phase 1 choices as a hard filter. Do not propose a skill or hook if they opted out of that artifact type.

## Phase 4: Write guidance files

Create or propose changes to DEEPSEEK.md and/or DEEPSEEK.local.md.

For DEEPSEEK.md:
- Include commands DeepSeek Code cannot guess, project-specific architecture notes, non-obvious testing quirks, repo etiquette, required setup, and important AI-tool rules from existing config files.
- Exclude file-by-file structure, standard language conventions, generic advice, long tutorials, and frequently changing information better referenced via @path.
- If CLAUDE.md already exists, do not overwrite it. Instead preserve it and create DEEPSEEK.md or propose a migration diff.

For DEEPSEEK.local.md:
- Include private preferences and local details only.
- Add DEEPSEEK.local.md to .gitignore.
- If compatibility with existing Claude Code setups matters, mention that CLAUDE.local.md can import or mirror the same private file, but do not put personal imports in team-shared files.

## Phase 5: Skills and hooks

If requested, create project skills under .deepseek/skills/<skill-name>/SKILL.md. If a repo already uses .claude/skills, preserve compatibility by reading those first and avoid overwriting them.

If hooks are requested, prefer .deepseek/settings.json. If the repo already uses .claude/settings.json, preserve compatibility and explain which file is authoritative.

## Phase 6: Summary

Summarize files written, key guidance included, and any follow-up suggestions. Keep the final response concise and specific to this repo.
"""


def _new_init_enabled() -> bool:
    return os.getenv("USER_TYPE") == "ant" or str(os.getenv("DEEPSEEK_CODE_NEW_INIT", "")).lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


async def getPromptForCommand(args: str = "", context: Any | None = None) -> list[dict[str, str]]:
    cwd = context.get("cwd") if isinstance(context, dict) else None
    maybeMarkProjectOnboardingComplete(cwd)
    prompt = NEW_INIT_PROMPT if _new_init_enabled() else OLD_INIT_PROMPT
    if args and args.strip():
        prompt += f"\n\n## Additional user instructions\n\n{args.strip()}"
    return [{"type": "text", "text": prompt}]


init = {
    "type": "prompt",
    "name": "init",
    "description": "Initialize DeepSeek Code repository guidance files and optional skills/hooks",
    "contentLength": 0,
    "progressMessage": "analyzing your codebase",
    "source": "builtin",
    "getPromptForCommand": getPromptForCommand,
}

default = init
