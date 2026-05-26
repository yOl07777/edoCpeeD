"""Conversation export command."""

from __future__ import annotations

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Awaitable, Callable

from python_src.utils.exportRenderer import renderMessagesToPlainText
from python_src.utils.slowOperations import writeFileSync_DEPRECATED

DoneCallback = Callable[[Any], Any | Awaitable[Any]]


def formatTimestamp(date: datetime | None = None) -> str:
    return (date or datetime.now()).strftime("%Y-%m-%d-%H%M%S")


def extractFirstPrompt(messages: list[dict[str, Any]] | None = None) -> str:
    for msg in messages or []:
        if not isinstance(msg, dict) or msg.get("type") != "user":
            continue
        payload = msg.get("message", {})
        content = payload.get("content") if isinstance(payload, dict) else payload
        result = ""
        if isinstance(content, str):
            result = content.strip()
        elif isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    result = str(item.get("text", "")).strip()
                    break
        result = result.splitlines()[0] if result else ""
        return result[:49] + "..." if len(result) > 50 else result
    return ""


def sanitizeFilename(text: str) -> str:
    text = re.sub(r"[^a-z0-9\s-]", "", text.lower())
    text = re.sub(r"\s+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


async def _notify(onDone: DoneCallback | None, payload: Any) -> None:
    if onDone is None:
        return
    result = onDone(payload)
    if hasattr(result, "__await__"):
        await result


async def exportWithReactRenderer(context: dict[str, Any] | Any) -> str:
    messages = context.get("messages", []) if isinstance(context, dict) else getattr(context, "messages", [])
    options = context.get("options", {}) if isinstance(context, dict) else getattr(context, "options", {})
    tools = options.get("tools", []) if isinstance(options, dict) else []
    return await renderMessagesToPlainText(messages, tools)


async def call(onDone: DoneCallback | None = None, context: dict[str, Any] | Any = None, args: str | None = "") -> dict[str, Any] | None:
    context = context or {}
    content = await exportWithReactRenderer(context)
    filename = (args or "").strip()
    cwd = Path(context.get("cwd") if isinstance(context, dict) and context.get("cwd") else os.getcwd())
    if filename:
        final = filename if filename.endswith(".txt") else re.sub(r"\.[^.]+$", "", filename) + ".txt"
        path = cwd / final
        try:
            writeFileSync_DEPRECATED(path, content, {"encoding": "utf-8", "flush": True})
            await _notify(onDone, f"Conversation exported to: {path}")
            return None
        except Exception as exc:
            await _notify(onDone, f"Failed to export conversation: {exc}")
            return None

    messages = context.get("messages", []) if isinstance(context, dict) else getattr(context, "messages", [])
    first_prompt = extractFirstPrompt(messages)
    timestamp = formatTimestamp()
    sanitized = sanitizeFilename(first_prompt)
    default_filename = f"{timestamp}-{sanitized}.txt" if sanitized else f"conversation-{timestamp}.txt"
    return {"type": "export_dialog", "content": content, "defaultFilename": default_filename}
