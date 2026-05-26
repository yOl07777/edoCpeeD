"""Prompt templates for background memory extraction."""

from __future__ import annotations

from typing import Any

from python_src.memdir.memoryTypes import (
    MEMORY_FRONTMATTER_EXAMPLE,
    TYPES_SECTION_COMBINED,
    TYPES_SECTION_INDIVIDUAL,
    WHAT_NOT_TO_SAVE_SECTION,
)


def _opener(newMessageCount: int, existingMemories: str) -> str:
    manifest = (
        f"\n\n## Existing memory files\n\n{existingMemories}\n\n"
        "Check this list before writing. Update an existing file rather than creating a duplicate."
        if existingMemories
        else ""
    )
    return "\n".join(
        [
            f"You are now acting as the memory extraction subagent for DeepSeek Code. Analyze the most recent ~{newMessageCount} messages above and update persistent memories.",
            "",
            "Available tools: Read, Grep, Glob, read-only Bash/run_shell, and Edit/Write for paths inside the memory directory only. Write-capable shell commands are not permitted.",
            "",
            "You have a limited turn budget. Read all candidate files first, then issue all writes/edits together. Do not investigate unrelated source files or run git commands.",
            "",
            f"You MUST only use content from the last ~{newMessageCount} messages to update memory.{manifest}",
        ]
    )


def _how_to_save(skipIndex: bool, *, team: bool = False) -> list[str]:
    target = "in the chosen private or team directory" if team else "to its own file"
    lines = [
        "## How to save memories",
        "",
        f"Write each memory {target} using this frontmatter format:",
        "",
        *MEMORY_FRONTMATTER_EXAMPLE,
        "",
        "- Organize memory semantically by topic, not chronologically.",
        "- Update or remove memories that turn out to be wrong or outdated.",
        "- Do not write duplicate memories.",
    ]
    if not skipIndex:
        lines.extend(
            [
                "- Also update `MEMORY.md`; it is an index, not a memory. Each entry should be one short line: `- [Title](file.md) - one-line hook`.",
                "- Keep `MEMORY.md` concise; future sessions may truncate long indexes.",
            ]
        )
    return lines


async def buildExtractAutoOnlyPrompt(
    newMessageCount: int,
    existingMemories: str = "",
    skipIndex: bool = False,
    *_: Any,
    **__: Any,
) -> str:
    return "\n".join(
        [
            _opener(int(newMessageCount), existingMemories),
            "",
            "If the user explicitly asks you to remember something, save it immediately. If they ask you to forget something, remove the relevant memory.",
            "",
            *TYPES_SECTION_INDIVIDUAL,
            *WHAT_NOT_TO_SAVE_SECTION,
            "",
            *_how_to_save(bool(skipIndex)),
        ]
    )


async def buildExtractCombinedPrompt(
    newMessageCount: int,
    existingMemories: str = "",
    skipIndex: bool = False,
    *_: Any,
    **__: Any,
) -> str:
    return "\n".join(
        [
            _opener(int(newMessageCount), existingMemories),
            "",
            "If the user explicitly asks you to remember something, save it immediately. If they ask you to forget something, remove the relevant memory.",
            "",
            *TYPES_SECTION_COMBINED,
            *WHAT_NOT_TO_SAVE_SECTION,
            "- Never save sensitive data such as API keys, passwords, or private credentials in team memory.",
            "",
            *_how_to_save(bool(skipIndex), team=True),
        ]
    )


__all__ = ["buildExtractAutoOnlyPrompt", "buildExtractCombinedPrompt"]
