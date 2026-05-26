"""
Local attachment helpers migrated from `src/utils/attachments.ts`.

The TypeScript module coordinates many UI/runtime inputs before model turns.
This Python shim keeps that boundary importable and testable without starting
watchers, querying models, or reaching remote services.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
import re
from typing import Any, Iterable

from python_src.tools.path_utils import resolve_workspace_path

AUTO_MODE_ATTACHMENT_CONFIG = {"kind": "auto-mode", "enabled": True}
PLAN_MODE_ATTACHMENT_CONFIG = {"kind": "plan-mode", "enabled": True}
RELEVANT_MEMORIES_CONFIG = {"kind": "relevant-memories", "max_files": 5}
TODO_REMINDER_CONFIG = {"kind": "todo-reminder", "turn_interval": 8}
VERIFY_PLAN_REMINDER_CONFIG = {"kind": "verify-plan-reminder", "turn_interval": 6}

_MENTION_RE = re.compile(r"(?<![\w.])@(?P<target>[^\s@]+)")
_MCP_URI_RE = re.compile(r"\bmcp://[^\s)>\]]+")
_LINE_RE = re.compile(r"^(?P<path>.+?):(?P<start>\d+)(?:-(?P<end>\d+))?$")
_SENT_SKILL_NAMES: set[str] = set()
_SUPPRESS_NEXT_SKILL_LISTING = False
_PREFETCH_CACHE: dict[str, Any] = {}


def _uniq(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        clean = str(value).strip().strip(".,;)")
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return result


def _as_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, (tuple, set)):
        return list(value)
    return [value]


def _attachment(kind: str, title: str, content: str = "", **fields: Any) -> dict[str, Any]:
    payload = {"type": kind, "kind": kind, "title": title, "content": content}
    payload.update(fields)
    return payload


def _preview(text: Any, limit: int = 400) -> str:
    content = "" if text is None else str(text)
    return content if len(content) <= limit else content[:limit] + "...[truncated]"


async def collectRecentSuccessfulTools(messages: Iterable[dict[str, Any]] | None = None, limit: int = 5) -> list[dict[str, Any]]:
    tools: list[dict[str, Any]] = []
    for message in _as_list(messages):
        if not isinstance(message, dict):
            continue
        status = message.get("status", message.get("ok", True))
        if status in {False, "error", "failed", "timed_out"}:
            continue
        name = message.get("tool") or message.get("name") or message.get("tool_name")
        if not name:
            continue
        tools.append(
            {
                "name": str(name),
                "status": "success",
                "summary": _preview(message.get("summary") or message.get("content") or message.get("output"), 160),
            }
        )
    return tools[-max(0, limit) :]


async def collectSurfacedMemories(memories: Iterable[Any] | None = None, limit: int = 5) -> list[dict[str, Any]]:
    attachments = await memoryFilesToAttachments(list(_as_list(memories))[:limit])
    return await filterDuplicateMemoryAttachments(attachments)


async def createAttachmentMessage(attachments: Iterable[dict[str, Any]] | None = None, role: str = "system") -> dict[str, Any]:
    items = [item for item in _as_list(attachments) if isinstance(item, dict)]
    lines = [f"[{item.get('type', 'attachment')}] {item.get('title', 'Untitled')}" for item in items]
    return {"role": role, "type": "attachment_message", "content": "\n".join(lines), "attachments": items}


async def extractAgentMentions(text: str = "") -> list[str]:
    agents: list[str] = []
    for target in _MENTION_RE.findall(text or ""):
        if target.startswith("agent:"):
            agents.append(target.split(":", 1)[1])
        elif target.startswith("agents/"):
            agents.append(Path(target).stem)
    return _uniq(agents)


async def extractAtMentionedFiles(text: str = "") -> list[str]:
    files: list[str] = []
    for target in _MENTION_RE.findall(text or ""):
        if target.startswith(("agent:", "mcp:", "agents/")) or "://" in target:
            continue
        files.append(_LINE_RE.match(target).group("path") if _LINE_RE.match(target) else target)
    return _uniq(files)


async def extractMcpResourceMentions(text: str = "") -> list[str]:
    values = [target[4:] for target in _MENTION_RE.findall(text or "") if target.startswith("mcp:")]
    values.extend(_MCP_URI_RE.findall(text or ""))
    return _uniq(values)


async def filterDuplicateMemoryAttachments(attachments: Iterable[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in _as_list(attachments):
        if not isinstance(item, dict):
            continue
        key = str(item.get("path") or item.get("name") or item.get("title") or item.get("content", ""))
        if key in seen:
            continue
        seen.add(key)
        result.append(item)
    return result


async def filterToBundledAndMcp(attachments: Iterable[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in _as_list(attachments):
        if not isinstance(item, dict):
            continue
        source = str(item.get("source", ""))
        kind = str(item.get("type", item.get("kind", "")))
        if source in {"bundled", "mcp"} or kind.startswith("mcp"):
            result.append(item)
    return result


async def generateFileAttachment(path: str | Path, cwd: str | Path | None = None, max_chars: int = 20_000) -> dict[str, Any]:
    resolved = resolve_workspace_path(str(path), cwd=str(cwd) if cwd is not None else None)
    pdf = await tryGetPDFReference(resolved)
    if pdf is not None:
        return pdf
    content = resolved.read_text(encoding="utf-8", errors="replace")
    truncated = len(content) > max_chars
    shown = content[:max_chars]
    return _attachment(
        "file",
        resolved.name,
        shown,
        path=str(resolved),
        relative_path=str(path),
        bytes=resolved.stat().st_size,
        truncated=truncated,
        source="workspace",
    )


async def getAgentListingDeltaAttachment(agents: Iterable[Any] | None = None) -> dict[str, Any]:
    items = [item if isinstance(item, dict) else {"name": str(item)} for item in _as_list(agents)]
    names = [str(item.get("name", "agent")) for item in items]
    return _attachment("agent-listing-delta", "Available agents", "\n".join(names), agents=items, count=len(items))


async def getAgentPendingMessageAttachments(messages: Iterable[dict[str, Any]] | None = None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, message in enumerate(_as_list(messages), start=1):
        if isinstance(message, dict):
            result.append(_attachment("agent-pending-message", f"Pending agent message {index}", _preview(message.get("text") or message.get("content"), 500), message=message))
    return result


async def getAttachments(
    prompt: str = "",
    *,
    cwd: str | Path | None = None,
    files: Iterable[str | Path] | None = None,
    memories: Iterable[Any] | None = None,
    queued_commands: Iterable[Any] | None = None,
    max_file_chars: int = 20_000,
) -> list[dict[str, Any]]:
    attachments: list[dict[str, Any]] = []
    for file_path in [*await extractAtMentionedFiles(prompt), *[str(item) for item in _as_list(files)]]:
        try:
            attachments.append(await generateFileAttachment(file_path, cwd=cwd, max_chars=max_file_chars))
        except (FileNotFoundError, PermissionError, OSError) as exc:
            attachments.append(_attachment("file-error", str(file_path), str(exc), path=str(file_path), error=str(exc)))
    attachments.extend(await collectSurfacedMemories(memories))
    attachments.extend(await getQueuedCommandAttachments(queued_commands))
    return attachments


async def getChangedFiles(files: Iterable[str] | None = None, diff: str | None = None) -> list[str]:
    values = [str(item) for item in _as_list(files)]
    if diff:
        values.extend(match.group(1) for match in re.finditer(r"^diff --git a/.+? b/(.+)$", diff, re.MULTILINE))
    return _uniq(values)


async def getCompactionReminderAttachment(message_count: int = 0, threshold: int = 40) -> dict[str, Any] | None:
    if message_count < threshold:
        return None
    return _attachment("compaction-reminder", "Conversation compaction", f"{message_count} messages in context; consider summarizing older turns.", message_count=message_count, threshold=threshold)


async def getContextEfficiencyAttachment(used_tokens: int = 0, max_tokens: int = 1, threshold: float = 0.8) -> dict[str, Any]:
    ratio = 0.0 if max_tokens <= 0 else used_tokens / max_tokens
    return _attachment("context-efficiency", "Context usage", f"{ratio:.0%} of context used.", used_tokens=used_tokens, max_tokens=max_tokens, ratio=ratio, above_threshold=ratio >= threshold)


async def getDateChangeAttachments(previous: str | date | None = None, current: str | date | None = None) -> list[dict[str, Any]]:
    today = current or date.today().isoformat()
    if previous is None or str(previous) == str(today):
        return []
    return [_attachment("date-change", "Date changed", f"Date changed from {previous} to {today}.", previous=str(previous), current=str(today))]


async def getDeferredToolsDeltaAttachment(tools: Iterable[Any] | None = None) -> dict[str, Any] | None:
    items = [item if isinstance(item, dict) else {"name": str(item)} for item in _as_list(tools)]
    if not items:
        return None
    return _attachment("deferred-tools-delta", "Deferred tools", "\n".join(str(item.get("name", "tool")) for item in items), tools=items, count=len(items))


async def getDirectoriesToProcess(paths: Iterable[str | Path] | None = None, cwd: str | Path | None = None) -> list[str]:
    dirs: list[str] = []
    for item in _as_list(paths):
        path = Path(item)
        if not path.is_absolute() and cwd is not None:
            path = Path(cwd) / path
        dirs.append(str((path if path.suffix == "" else path.parent).resolve()))
    return _uniq(dirs)


async def getMcpInstructionsDeltaAttachment(instructions: str | dict[str, Any] | None = None) -> dict[str, Any] | None:
    if not instructions:
        return None
    if isinstance(instructions, dict):
        content = _preview(instructions.get("content") or instructions.get("instructions"), 2000)
        server = instructions.get("server")
    else:
        content = _preview(instructions, 2000)
        server = None
    return _attachment("mcp-instructions-delta", "MCP instructions", content, server=server, source="mcp")


async def getQueuedCommandAttachments(commands: Iterable[Any] | None = None) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for index, command in enumerate(_as_list(commands), start=1):
        payload = command if isinstance(command, dict) else {"command": str(command)}
        content = str(payload.get("command") or payload.get("text") or "")
        result.append(_attachment("queued-command", f"Queued command {index}", content, command=payload))
    return result


async def getVerifyPlanReminderTurnCount(turn_count: int = 0, interval: int | None = None) -> int:
    every = interval or VERIFY_PLAN_REMINDER_CONFIG["turn_interval"]
    return max(0, every - (turn_count % every))


async def memoryFilesToAttachments(files: Iterable[Any] | None = None, cwd: str | Path | None = None, max_chars: int = 8000) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for item in _as_list(files):
        if isinstance(item, dict):
            title = str(item.get("name") or item.get("title") or item.get("path") or "Memory")
            content = _preview(item.get("content", ""), max_chars)
            attachment = _attachment("memory", title, content)
            attachment.update(item)
            attachment["type"] = "memory"
            attachment["kind"] = "memory"
            result.append(attachment)
            continue
        try:
            path = resolve_workspace_path(str(item), cwd=str(cwd) if cwd is not None else None)
            content = path.read_text(encoding="utf-8", errors="replace")
            result.append(_attachment("memory", _memory_header(path), content[:max_chars], path=str(path), truncated=len(content) > max_chars, source="memory"))
        except (FileNotFoundError, PermissionError, OSError) as exc:
            result.append(_attachment("memory-error", str(item), str(exc), path=str(item), error=str(exc)))
    return result


def _memory_header(memory: str | Path | dict[str, Any]) -> str:
    if isinstance(memory, dict):
        name = memory.get("name") or memory.get("title") or memory.get("path") or "Memory"
    else:
        name = Path(memory).name
    return f"# Memory: {name}"


async def memoryHeader(memory: str | Path | dict[str, Any]) -> str:
    return _memory_header(memory)


async def parseAtMentionedFileLines(text: str = "") -> list[dict[str, Any]]:
    parsed: list[dict[str, Any]] = []
    for target in _MENTION_RE.findall(text or ""):
        if target.startswith(("agent:", "mcp:", "agents/")) or "://" in target:
            continue
        match = _LINE_RE.match(target)
        if not match:
            parsed.append({"path": target})
            continue
        start = int(match.group("start"))
        item: dict[str, Any] = {"path": match.group("path"), "line": start, "start": start}
        if match.group("end"):
            item["end"] = int(match.group("end"))
        parsed.append(item)
    return parsed


async def readMemoriesForSurfacing(paths: Iterable[str | Path] | None = None, cwd: str | Path | None = None, max_chars: int = 8000) -> list[dict[str, Any]]:
    return await memoryFilesToAttachments(paths, cwd=cwd, max_chars=max_chars)


async def resetSentSkillNames() -> dict[str, Any]:
    count = len(_SENT_SKILL_NAMES)
    _SENT_SKILL_NAMES.clear()
    return {"reset": True, "cleared": count}


async def startRelevantMemoryPrefetch(memories: Iterable[Any] | None = None, query: str = "") -> dict[str, Any]:
    attachments = await collectSurfacedMemories(memories)
    _PREFETCH_CACHE.clear()
    _PREFETCH_CACHE.update({"query": query, "attachments": attachments, "count": len(attachments)})
    return dict(_PREFETCH_CACHE)


async def suppressNextSkillListing(value: bool = True) -> dict[str, Any]:
    global _SUPPRESS_NEXT_SKILL_LISTING
    _SUPPRESS_NEXT_SKILL_LISTING = bool(value)
    return {"suppressed": _SUPPRESS_NEXT_SKILL_LISTING}


async def tryGetPDFReference(path: str | Path) -> dict[str, Any] | None:
    resolved = Path(path)
    if resolved.suffix.lower() != ".pdf":
        return None
    return _attachment(
        "pdf",
        resolved.name,
        f"PDF reference: {resolved}",
        path=str(resolved),
        mime_type="application/pdf",
        source="workspace",
    )


__all__ = [
    "AUTO_MODE_ATTACHMENT_CONFIG",
    "PLAN_MODE_ATTACHMENT_CONFIG",
    "RELEVANT_MEMORIES_CONFIG",
    "TODO_REMINDER_CONFIG",
    "VERIFY_PLAN_REMINDER_CONFIG",
    "collectRecentSuccessfulTools",
    "collectSurfacedMemories",
    "createAttachmentMessage",
    "extractAgentMentions",
    "extractAtMentionedFiles",
    "extractMcpResourceMentions",
    "filterDuplicateMemoryAttachments",
    "filterToBundledAndMcp",
    "generateFileAttachment",
    "getAgentListingDeltaAttachment",
    "getAgentPendingMessageAttachments",
    "getAttachments",
    "getChangedFiles",
    "getCompactionReminderAttachment",
    "getContextEfficiencyAttachment",
    "getDateChangeAttachments",
    "getDeferredToolsDeltaAttachment",
    "getDirectoriesToProcess",
    "getMcpInstructionsDeltaAttachment",
    "getQueuedCommandAttachments",
    "getVerifyPlanReminderTurnCount",
    "memoryFilesToAttachments",
    "memoryHeader",
    "parseAtMentionedFileLines",
    "readMemoriesForSurfacing",
    "resetSentSkillNames",
    "startRelevantMemoryPrefetch",
    "suppressNextSkillListing",
    "tryGetPDFReference",
]
