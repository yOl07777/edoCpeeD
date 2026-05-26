from __future__ import annotations

import re
from typing import Any

from python_src.components._shared import component_payload, option, scalar_arg


def _blocks(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    in_code = False
    code_lang = ""
    code_lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("```"):
            if in_code:
                rows.append({"type": "code", "language": code_lang, "text": "\n".join(code_lines)})
                in_code = False
                code_lang = ""
                code_lines = []
            else:
                in_code = True
                code_lang = line[3:].strip()
            continue
        if in_code:
            code_lines.append(line)
        elif line.startswith("#"):
            rows.append({"type": "heading", "level": len(line) - len(line.lstrip("#")), "text": line.lstrip("#").strip()})
        elif re.match(r"^\s*[-*]\s+", line):
            rows.append({"type": "list_item", "text": re.sub(r"^\s*[-*]\s+", "", line)})
        elif line.strip():
            rows.append({"type": "paragraph", "text": line.strip()})
    if in_code:
        rows.append({"type": "code", "language": code_lang, "text": "\n".join(code_lines)})
    return rows


async def Markdown(*args: Any, **kwargs: Any) -> Any:
    text = str(option(args, kwargs, "text", option(args, kwargs, "children", scalar_arg(args, ""))))
    blocks = _blocks(text)
    return component_payload("markdown", text=text, blocks=blocks, blockCount=len(blocks))


async def StreamingMarkdown(*args: Any, **kwargs: Any) -> Any:
    rendered = await Markdown(*args, **kwargs)
    rendered["type"] = "streaming_markdown"
    rendered["streaming"] = bool(option(args, kwargs, "streaming", True))
    return rendered


__all__ = ["Markdown", "StreamingMarkdown"]
