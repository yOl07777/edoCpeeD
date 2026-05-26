"""Prompt construction for combined private/team memory."""

from __future__ import annotations

from typing import Iterable

from .memdir import DIRS_EXIST_GUIDANCE, ENTRYPOINT_NAME, MAX_ENTRYPOINT_LINES, buildSearchingPastContextSection
from .memoryTypes import (
    MEMORY_DRIFT_CAVEAT,
    MEMORY_FRONTMATTER_EXAMPLE,
    TRUSTING_RECALL_SECTION,
    TYPES_SECTION_COMBINED,
    WHAT_NOT_TO_SAVE_SECTION,
)
from .paths import getAutoMemPath
from .teamMemPaths import getTeamMemPath


def buildCombinedMemoryPrompt(extraGuidelines: Iterable[str] | None = None, skipIndex: bool = False) -> str:
    """Build the memory system prompt for private plus team memory."""

    auto_dir = getAutoMemPath()
    team_dir = getTeamMemPath()
    if skipIndex:
        how_to_save = [
            "## How to save memories",
            "",
            "Write each memory to its own file in the chosen directory using this frontmatter format:",
            "",
            *MEMORY_FRONTMATTER_EXAMPLE,
            "",
            "- Keep name, description, and type fields up to date.",
            "- Organize memory semantically by topic, not chronologically.",
            "- Update or remove memories that turn out to be wrong or outdated.",
            "- Do not write duplicate memories; update an existing memory when possible.",
        ]
    else:
        how_to_save = [
            "## How to save memories",
            "",
            "Saving a memory is a two-step process:",
            "",
            "**Step 1** - write the memory to its own file in the chosen directory using this frontmatter format:",
            "",
            *MEMORY_FRONTMATTER_EXAMPLE,
            "",
            (
                f"**Step 2** - add a one-line pointer to that file in the same directory's `{ENTRYPOINT_NAME}`. "
                f"Each directory has its own `{ENTRYPOINT_NAME}` index; keep entries under about 150 characters."
            ),
            "",
            f"- `{ENTRYPOINT_NAME}` indexes are loaded into context; lines after {MAX_ENTRYPOINT_LINES} are truncated.",
            "- Keep name, description, and type fields up to date.",
            "- Organize memory semantically by topic, not chronologically.",
            "- Update or remove memories that turn out to be wrong or outdated.",
            "- Do not write duplicate memories; update an existing memory when possible.",
        ]

    lines = [
        "# Memory",
        "",
        (
            "You have a persistent, file-based memory system with two directories: "
            f"a private directory at `{auto_dir}` and a shared team directory at `{team_dir}`. {DIRS_EXIST_GUIDANCE}"
        ),
        "",
        "Build this memory system over time so future conversations retain useful context without re-learning it.",
        "",
        "If the user explicitly asks you to remember something, save it immediately as the best-fitting type. "
        "If they ask you to forget something, find and remove the relevant entry.",
        "",
        "## Memory scope",
        "",
        "- private: memories between DeepSeek Code and the current user.",
        "- team: memories shared by users working in this project directory.",
        "",
        *TYPES_SECTION_COMBINED,
        *WHAT_NOT_TO_SAVE_SECTION,
        "- Never save API keys, credentials, or sensitive personal data in shared team memories.",
        "",
        *how_to_save,
        "",
        "## When to access memories",
        "- When personal or team memories seem relevant, or the user references prior work.",
        "- You MUST access memory when the user explicitly asks you to check, recall, or remember.",
        "- If the user says to ignore memory, proceed as if memory were empty.",
        MEMORY_DRIFT_CAVEAT,
        "",
        *TRUSTING_RECALL_SECTION,
        "",
        "## Memory and other forms of persistence",
        "Use plans and tasks for current-conversation work. Use memory only for information useful in future conversations.",
        *(list(extraGuidelines or [])),
        "",
        buildSearchingPastContextSection(auto_dir),
    ]
    return "\n".join(lines)


__all__ = ["buildCombinedMemoryPrompt"]
