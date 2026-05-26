"""Prompt templates for Magic Docs updates."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any


def _default_template() -> str:
    return """IMPORTANT: This message and these instructions are NOT part of the actual user conversation. Do NOT include references to documentation updates or Magic Docs in the document content.

Based on the user conversation above, update the Magic Doc file to incorporate NEW learnings that are valuable to preserve.

The file {{docPath}} has already been read for you. Here are its current contents:
<current_doc_content>
{{docContents}}
</current_doc_content>

Document title: {{docTitle}}
{{customInstructions}}

Your ONLY task is to use the Edit tool to update the documentation file if there is substantial new information to add, then stop. If there is nothing substantial to add, respond briefly and do not call tools.

CRITICAL RULES:
- Preserve the Magic Doc header exactly: # MAGIC DOC: {{docTitle}}
- Preserve any italicized instruction line immediately after the header.
- Keep the document current; it is not a changelog.
- Update information in-place; remove outdated content.
- Be terse and high-signal.
- Document architecture, entry points, non-obvious patterns, and design rationale.
- Do not duplicate obvious source-code details.

Use the Edit tool with file_path: {{docPath}}"""


async def _load_template() -> str:
    root = os.getenv("DEEPCODE_CONFIG_HOME") or os.getenv("DEEPSEEK_CONFIG_DIR") or str(Path.home() / ".deepseek")
    path = Path(root) / "magic-docs" / "prompt.md"
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return _default_template()


def _substitute(template: str, variables: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return variables.get(key, match.group(0))

    return re.sub(r"\{\{(\w+)\}\}", replace, template)


async def buildMagicDocsUpdatePrompt(
    docContents: str,
    docPath: str,
    docTitle: str,
    instructions: str | None = None,
    *_: Any,
    **__: Any,
) -> str:
    custom = (
        "\n\nDOCUMENT-SPECIFIC UPDATE INSTRUCTIONS:\n"
        "The document author has provided specific instructions. These take priority over the general rules:\n\n"
        f'"{instructions}"'
        if instructions
        else ""
    )
    return _substitute(
        await _load_template(),
        {
            "docContents": docContents,
            "docPath": docPath,
            "docTitle": docTitle,
            "customInstructions": custom,
        },
    )


__all__ = ["buildMagicDocsUpdatePrompt"]
