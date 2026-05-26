"""Prompt builder for background memory consolidation."""

from __future__ import annotations

from typing import Any


ENTRYPOINT_NAME = "MEMORY.md"
MAX_ENTRYPOINT_LINES = 200
DIR_EXISTS_GUIDANCE = "If the directory does not exist, create it before writing memory files."


async def buildConsolidationPrompt(memoryRoot: str, transcriptDir: str, extra: str = "", *_: Any, **__: Any) -> str:
    suffix = f"\n\n## Additional context\n\n{extra}" if extra else ""
    return f"""# Dream: Memory Consolidation

You are performing a dream: a reflective pass over your memory files. Synthesize what you learned recently into durable, well-organized memories so future DeepSeek Code sessions can orient quickly.

Memory directory: `{memoryRoot}`
{DIR_EXISTS_GUIDANCE}

Session transcripts: `{transcriptDir}` (large JSONL files; grep narrowly, do not read whole files)

---

## Phase 1: Orient

- List the memory directory to see what already exists.
- Read `{ENTRYPOINT_NAME}` to understand the current index.
- Skim existing topic files so you improve them rather than creating duplicates.
- If `logs/` or `sessions/` subdirectories exist, review recent entries there.

## Phase 2: Gather Recent Signal

Look for new information worth persisting. Prefer daily logs, existing memories that drifted, and narrow transcript searches for specific context.

## Phase 3: Consolidate

For each thing worth remembering, write or update a top-level memory file. Merge new signal into existing topic files, convert relative dates to absolute dates, and delete contradicted facts at the source.

## Phase 4: Prune And Index

Update `{ENTRYPOINT_NAME}` so it stays under {MAX_ENTRYPOINT_LINES} lines and under about 25KB. It is an index, not a dump. Keep entries short: `- [Title](file.md) - one-line hook`.

Return a brief summary of what you consolidated, updated, or pruned. If nothing changed, say so.{suffix}"""


__all__ = [
    "DIR_EXISTS_GUIDANCE",
    "ENTRYPOINT_NAME",
    "MAX_ENTRYPOINT_LINES",
    "buildConsolidationPrompt",
]
