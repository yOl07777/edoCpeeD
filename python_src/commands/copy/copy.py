"""Implementation for `/copy`."""

from __future__ import annotations

import re
import tempfile
from pathlib import Path
from typing import Any, Callable

MAX_LOOKBACK = 20
COPY_DIR = Path(tempfile.gettempdir()) / "deepseek-code"
RESPONSE_FILENAME = "response.md"


def _extract_text_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text" and isinstance(block.get("text"), str):
                    parts.append(block["text"])
                elif isinstance(block.get("content"), str):
                    parts.append(block["content"])
            elif isinstance(block, str):
                parts.append(block)
        return "\n\n".join(part for part in parts if part)
    return ""


def collectRecentAssistantTexts(messages: list[dict[str, Any]]) -> list[str]:
    texts: list[str] = []
    for msg in reversed(messages):
        if len(texts) >= MAX_LOOKBACK:
            break
        if not isinstance(msg, dict) or msg.get("type") != "assistant" or msg.get("isApiErrorMessage"):
            continue
        message = msg.get("message") if isinstance(msg.get("message"), dict) else {}
        text = _extract_text_content(message.get("content"))
        if text:
            texts.append(text)
    return texts


def fileExtension(lang: str | None) -> str:
    if lang:
        sanitized = re.sub(r"[^a-zA-Z0-9]", "", lang)
        if sanitized and sanitized != "plaintext":
            return f".{sanitized}"
    return ".txt"


def extractCodeBlocks(markdown: str) -> list[dict[str, str | None]]:
    pattern = re.compile(r"```([A-Za-z0-9_+.-]*)\n(.*?)```", re.DOTALL)
    return [{"lang": match.group(1) or None, "code": match.group(2).rstrip("\n")} for match in pattern.finditer(markdown)]


async def copyOrWriteToFile(text: str, filename: str = RESPONSE_FILENAME) -> dict[str, Any]:
    COPY_DIR.mkdir(parents=True, exist_ok=True)
    path = COPY_DIR / filename
    path.write_text(text, encoding="utf-8")
    return {"text": text, "filePath": str(path), "characters": len(text), "lines": text.count("\n") + 1}


async def call(
    onDone: Callable[..., Any] | None = None,
    context: dict[str, Any] | None = None,
    args: str = "",
    *,
    messages: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    source_messages = messages or (context or {}).get("messages", [])
    texts = collectRecentAssistantTexts(source_messages)
    if not texts:
        message = "No assistant response found to copy."
        if onDone:
            onDone(message)
        return {"ok": False, "message": message}
    try:
        age = max(0, int((args or "1").strip() or "1") - 1)
    except ValueError:
        age = 0
    text = texts[min(age, len(texts) - 1)]
    blocks = extractCodeBlocks(text)
    if blocks and (args or "").strip().lower() == "code":
        selected = blocks[0]
        result = await copyOrWriteToFile(str(selected["code"]), f"copy{fileExtension(selected['lang'])}")
    else:
        result = await copyOrWriteToFile(text, RESPONSE_FILENAME)
    message = f"Copied {result['characters']} characters to {result['filePath']}"
    if onDone:
        onDone(message)
    return {"ok": True, "message": message, "result": result, "codeBlocks": blocks}
