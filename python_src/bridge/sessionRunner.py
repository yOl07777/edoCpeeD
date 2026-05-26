"""Lightweight bridge session runner helpers."""

from __future__ import annotations

import asyncio
import json
import re
import time
from dataclasses import dataclass, field
from typing import Any, Callable

MAX_ACTIVITIES = 10
MAX_STDERR_LINES = 10

TOOL_VERBS = {
    "Read": "Reading",
    "Write": "Writing",
    "Edit": "Editing",
    "MultiEdit": "Editing",
    "Bash": "Running",
    "Glob": "Searching",
    "Grep": "Searching",
    "WebFetch": "Fetching",
    "WebSearch": "Searching",
    "Task": "Running task",
    "FileReadTool": "Reading",
    "FileWriteTool": "Writing",
    "FileEditTool": "Editing",
    "NotebookEditTool": "Editing notebook",
    "LSP": "LSP",
}


def safeFilenameId(id: str) -> str:
    return re.sub(r"[^a-zA-Z0-9_-]", "_", id)


def _tool_summary(name: str, input: dict[str, Any]) -> str:
    verb = TOOL_VERBS.get(name, name)
    target = (
        input.get("file_path")
        or input.get("filePath")
        or input.get("pattern")
        or str(input.get("command", ""))[:60]
        or input.get("url")
        or input.get("query")
        or ""
    )
    return f"{verb} {target}" if target else verb


def extractActivities(line: str, sessionId: str, onDebug: Callable[[str], None] | None = None) -> list[dict[str, Any]]:
    try:
        msg = json.loads(line)
    except ValueError:
        return []
    if not isinstance(msg, dict):
        return []
    activities: list[dict[str, Any]] = []
    now = time.time() * 1000
    if msg.get("type") == "assistant":
        message = msg.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                if block.get("type") == "tool_use":
                    name = str(block.get("name") or "Tool")
                    summary = _tool_summary(name, block.get("input") if isinstance(block.get("input"), dict) else {})
                    activities.append({"type": "tool_start", "summary": summary, "timestamp": now})
                elif block.get("type") == "text" and block.get("text"):
                    activities.append({"type": "text", "summary": str(block["text"])[:80], "timestamp": now})
    elif msg.get("type") == "result":
        subtype = msg.get("subtype")
        if subtype == "success":
            activities.append({"type": "result", "summary": "Session completed", "timestamp": now})
        elif subtype:
            errors = msg.get("errors")
            summary = errors[0] if isinstance(errors, list) and errors else f"Error: {subtype}"
            activities.append({"type": "error", "summary": summary, "timestamp": now})
    if onDebug and activities:
        onDebug(f"[bridge:activity] sessionId={sessionId} activities={len(activities)}")
    return activities


def _extract_user_message_text(msg: dict[str, Any]) -> str | None:
    if msg.get("parent_tool_use_id") is not None or msg.get("isSynthetic") or msg.get("isReplay"):
        return None
    message = msg.get("message")
    content = message.get("content") if isinstance(message, dict) else None
    text = None
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text")
                break
    return text.strip() if isinstance(text, str) and text.strip() else None


@dataclass
class InMemorySessionHandle:
    sessionId: str
    sdkUrl: str
    accessToken: str
    activities: list[dict[str, Any]] = field(default_factory=list)
    lastStderr: list[str] = field(default_factory=list)
    done: asyncio.Future[str] = field(default_factory=asyncio.Future)
    stdin: list[str] = field(default_factory=list)
    killed: bool = False

    @property
    def currentActivity(self) -> dict[str, Any] | None:
        return self.activities[-1] if self.activities else None

    def kill(self) -> None:
        self.killed = True
        if not self.done.done():
            self.done.set_result("interrupted")

    def forceKill(self) -> None:
        self.kill()

    def writeStdin(self, data: str) -> None:
        self.stdin.append(data)

    def updateAccessToken(self, token: str) -> None:
        self.accessToken = token
        self.writeStdin(json.dumps({"type": "update_environment_variables", "variables": {"CLAUDE_CODE_SESSION_ACCESS_TOKEN": token}}) + "\n")


class InMemorySessionSpawner:
    def __init__(self, deps: dict[str, Any]) -> None:
        self.deps = deps
        self.spawned: list[InMemorySessionHandle] = []

    def spawn(self, opts: dict[str, Any], dir: str) -> InMemorySessionHandle:
        handle = InMemorySessionHandle(
            sessionId=opts["sessionId"],
            sdkUrl=opts["sdkUrl"],
            accessToken=opts.get("accessToken", ""),
        )
        self.spawned.append(handle)
        on_debug = self.deps.get("onDebug")
        if callable(on_debug):
            on_debug(f"[bridge:session] prepared sessionId={handle.sessionId} dir={dir}")
        return handle


def createSessionSpawner(deps: dict[str, Any] | None = None, **kwargs: Any) -> InMemorySessionSpawner:
    merged = dict(deps or {})
    merged.update(kwargs)
    return InMemorySessionSpawner(merged)


_extractActivitiesForTesting = extractActivities
