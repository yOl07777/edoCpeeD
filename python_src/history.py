from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any


MAX_HISTORY_ITEMS = 100
MAX_PASTED_CONTENT_LENGTH = 1024
REFERENCE_RE = re.compile(r"\[(?:Pasted text|Image|\.\.\.Truncated text) #(\d+)(?: \+\d+ lines)?\.?\]")

_pending_entries: list[dict[str, Any]] = []
_last_added_entry: dict[str, Any] | None = None
_skipped_timestamps: set[int] = set()


def _project_root() -> str:
    try:
        from python_src.bootstrap import state

        return str(state.peekState("projectRoot") or Path.cwd())
    except Exception:
        return str(Path.cwd())


def _session_id() -> str:
    try:
        from python_src.bootstrap import state

        return str(state.peekState("sessionId") or "default")
    except Exception:
        return "default"


def _history_path() -> Path:
    base = Path(os.getenv("DEEPSEEK_CODE_HOME") or Path.cwd() / ".deepseek_code")
    base.mkdir(parents=True, exist_ok=True)
    return base / "history.jsonl"


def getPastedTextRefNumLines(text: str) -> int:
    return len(re.findall(r"\r\n|\r|\n", text))


def formatPastedTextRef(id: int, numLines: int) -> str:
    if numLines == 0:
        return f"[Pasted text #{id}]"
    return f"[Pasted text #{id} +{numLines} lines]"


def formatImageRef(id: int) -> str:
    return f"[Image #{id}]"


def parseReferences(input: str) -> list[dict[str, Any]]:
    return [
        {"id": int(match.group(1)), "match": match.group(0), "index": match.start()}
        for match in REFERENCE_RE.finditer(input or "")
        if int(match.group(1)) > 0
    ]


def expandPastedTextRefs(input: str, pastedContents: dict[int, dict[str, Any]] | dict[str, dict[str, Any]]) -> str:
    expanded = input
    for ref in reversed(parseReferences(input)):
        content = pastedContents.get(ref["id"]) or pastedContents.get(str(ref["id"]))
        if not isinstance(content, dict) or content.get("type") != "text":
            continue
        text = str(content.get("content", ""))
        expanded = expanded[: ref["index"]] + text + expanded[ref["index"] + len(ref["match"]) :]
    return expanded


def _serialize_pasted_contents(contents: dict[Any, dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    serialized: dict[str, dict[str, Any]] = {}
    for key, content in (contents or {}).items():
        if content.get("type") == "image":
            continue
        text = str(content.get("content", ""))
        serialized[str(key)] = {
            "id": int(content.get("id", key)),
            "type": content.get("type", "text"),
            "content": text[:MAX_PASTED_CONTENT_LENGTH],
            "truncated": len(text) > MAX_PASTED_CONTENT_LENGTH,
            "mediaType": content.get("mediaType"),
            "filename": content.get("filename"),
        }
    return serialized


def _append_entry(entry: dict[str, Any]) -> None:
    path = _history_path()
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


def addToHistory(command: dict[str, Any] | str) -> None:
    global _last_added_entry
    if os.getenv("CLAUDE_CODE_SKIP_PROMPT_HISTORY", "").lower() in {"1", "true", "yes"}:
        return
    entry = {"display": command, "pastedContents": {}} if isinstance(command, str) else dict(command)
    log_entry = {
        **entry,
        "pastedContents": _serialize_pasted_contents(entry.get("pastedContents")),
        "timestamp": int(time.time() * 1000),
        "project": _project_root(),
        "sessionId": _session_id(),
    }
    _pending_entries.append(log_entry)
    _last_added_entry = log_entry
    _append_entry(log_entry)


def clearPendingHistoryEntries() -> None:
    global _last_added_entry
    _pending_entries.clear()
    _last_added_entry = None
    _skipped_timestamps.clear()


def removeLastFromHistory() -> None:
    global _last_added_entry
    if _last_added_entry is None:
        return
    entry = _last_added_entry
    _last_added_entry = None
    try:
        _pending_entries.remove(entry)
    except ValueError:
        _skipped_timestamps.add(int(entry.get("timestamp", 0)))


async def makeHistoryReader():
    current_project = _project_root()
    yielded = 0
    lines: list[str] = []
    path = _history_path()
    if path.exists():
        lines = path.read_text(encoding="utf-8").splitlines()
    for line in reversed(lines):
        if yielded >= MAX_HISTORY_ITEMS:
            return
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if entry.get("project") != current_project:
            continue
        if entry.get("timestamp") in _skipped_timestamps:
            continue
        yielded += 1
        yield {"display": entry.get("display", ""), "pastedContents": entry.get("pastedContents", {})}
