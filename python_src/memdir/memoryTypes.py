"""Memory type taxonomy used by DeepSeek Code memory directories."""

from __future__ import annotations

from typing import Any, Literal

MemoryType = Literal["user", "feedback", "project", "reference"]

MEMORY_TYPES: tuple[MemoryType, ...] = ("user", "feedback", "project", "reference")

TYPES_SECTION_INDIVIDUAL = [
    "## Types of memory",
    "",
    "There are several discrete types of memory that can be stored: user, feedback, project, and reference.",
]

TYPES_SECTION_COMBINED = [
    "## Types of memory",
    "",
    "Memories may be private or team-scoped. Choose the narrowest scope that still helps future work.",
]

WHAT_NOT_TO_SAVE_SECTION = [
    "## What NOT to save in memory",
    "",
    "- Code patterns, architecture, file paths, or project structure that can be derived from the current repo.",
    "- Git history or recent changes that are better answered with git.",
    "- Ephemeral task details from the current conversation.",
]

MEMORY_DRIFT_CAVEAT = (
    "- Memory records can become stale over time. Verify current files or resources before acting on old memory."
)

WHEN_TO_ACCESS_SECTION = [
    "## When to access memories",
    "- When memories seem relevant, or the user explicitly asks you to recall or remember.",
    "- If the user says to ignore memory, proceed as if no memory exists.",
    MEMORY_DRIFT_CAVEAT,
]

TRUSTING_RECALL_SECTION = [
    "## Before recommending from memory",
    "",
    "A memory is a point-in-time claim. If it names a file, function, flag, or external resource, verify it first.",
]

MEMORY_FRONTMATTER_EXAMPLE = [
    "```markdown",
    "---",
    "name: {{memory name}}",
    "description: {{one-line description used for relevance selection}}",
    f"type: {{{', '.join(MEMORY_TYPES)}}}",
    "---",
    "",
    "{{memory content}}",
    "```",
]


async def parseMemoryType(raw: Any, *_args: Any, **_kwargs: Any) -> MemoryType | None:
    """Parse a raw frontmatter value into a supported memory type."""

    if not isinstance(raw, str):
        return None
    normalized = raw.strip().lower()
    return normalized if normalized in MEMORY_TYPES else None  # type: ignore[return-value]


__all__ = [
    "MEMORY_DRIFT_CAVEAT",
    "MEMORY_FRONTMATTER_EXAMPLE",
    "MEMORY_TYPES",
    "MemoryType",
    "TRUSTING_RECALL_SECTION",
    "TYPES_SECTION_COMBINED",
    "TYPES_SECTION_INDIVIDUAL",
    "WHAT_NOT_TO_SAVE_SECTION",
    "WHEN_TO_ACCESS_SECTION",
    "parseMemoryType",
]
