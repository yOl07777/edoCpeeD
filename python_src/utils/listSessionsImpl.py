"""List session JSONL files without pulling in the full CLI runtime."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from python_src.utils.sessionStoragePortable import (
    extractFirstPromptFromHead,
    extractJsonStringField,
    extractLastJsonStringField,
    findProjectDir,
    getProjectsDir,
    readSessionLite,
    validateUuid,
)


async def parseSessionInfoFromLite(
    sessionId: str,
    lite: dict[str, Any],
    projectPath: str | None = None,
) -> dict[str, Any] | None:
    head = lite.get("head") or ""
    tail = lite.get("tail") or ""
    first_line = head.splitlines()[0] if head.splitlines() else head
    if '"isSidechain":true' in first_line or '"isSidechain": true' in first_line:
        return None

    custom_title = (
        await extractLastJsonStringField(tail, "customTitle")
        or await extractLastJsonStringField(head, "customTitle")
        or await extractLastJsonStringField(tail, "aiTitle")
        or await extractLastJsonStringField(head, "aiTitle")
    )
    first_prompt = await extractFirstPromptFromHead(head)
    summary = (
        custom_title
        or await extractLastJsonStringField(tail, "lastPrompt")
        or await extractLastJsonStringField(tail, "summary")
        or first_prompt
    )
    if not summary:
        return None

    created_at = None
    first_timestamp = await extractJsonStringField(head, "timestamp")
    if first_timestamp:
        from datetime import datetime

        try:
            created_at = datetime.fromisoformat(first_timestamp.replace("Z", "+00:00")).timestamp() * 1000
        except ValueError:
            created_at = None

    tag = None
    for line in reversed(tail.splitlines()):
        try:
            data = json.loads(line)
        except Exception:
            continue
        if data.get("type") != "tag":
            continue
        value = data.get("tag")
        if isinstance(value, str):
            tag = value
            break

    return {
        "sessionId": sessionId,
        "summary": summary,
        "lastModified": lite.get("mtime", 0),
        "fileSize": lite.get("size"),
        "customTitle": custom_title,
        "firstPrompt": first_prompt,
        "gitBranch": await extractLastJsonStringField(tail, "gitBranch") or await extractJsonStringField(head, "gitBranch"),
        "cwd": await extractJsonStringField(head, "cwd") or projectPath,
        "tag": tag,
        "createdAt": created_at,
    }


async def listCandidates(projectDir: str | Path, doStat: bool, projectPath: str | None = None) -> list[dict[str, Any]]:
    root = Path(projectDir)
    if not root.exists():
        return []
    candidates: list[dict[str, Any]] = []
    for path in root.iterdir():
        if not path.is_file() or path.suffix != ".jsonl":
            continue
        session_id = await validateUuid(path.stem)
        if not session_id:
            continue
        mtime = path.stat().st_mtime * 1000 if doStat else 0
        candidates.append(
            {
                "sessionId": session_id,
                "filePath": str(path),
                "mtime": mtime,
                "projectPath": projectPath,
            }
        )
    return candidates


async def _read_candidate(candidate: dict[str, Any]) -> dict[str, Any] | None:
    lite = await readSessionLite(candidate["filePath"])
    if not lite:
        return None
    info = await parseSessionInfoFromLite(candidate["sessionId"], lite, candidate.get("projectPath"))
    if info and candidate.get("mtime"):
        info["lastModified"] = candidate["mtime"]
    return info


async def listSessionsImpl(options: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    opts = options or {}
    directory = opts.get("dir")
    limit = opts.get("limit")
    offset = int(opts.get("offset") or 0)
    do_stat = bool((isinstance(limit, int) and limit > 0) or offset > 0)

    candidates: list[dict[str, Any]] = []
    if directory:
        project_dir = await findProjectDir(directory) or str(Path(directory))
        candidates = await listCandidates(project_dir, do_stat, str(directory))
    else:
        projects = Path(await getProjectsDir())
        if projects.exists():
            for child in projects.iterdir():
                if child.is_dir():
                    candidates.extend(await listCandidates(child, do_stat))

    if do_stat:
        candidates.sort(key=lambda item: (item.get("mtime", 0), item.get("sessionId", "")), reverse=True)

    sessions = [info for info in [await _read_candidate(c) for c in candidates] if info]
    sessions.sort(key=lambda item: (item.get("lastModified", 0), item.get("sessionId", "")), reverse=True)

    deduped: dict[str, dict[str, Any]] = {}
    for session in sessions:
        deduped.setdefault(session["sessionId"], session)
    result = list(deduped.values())[offset:]
    if isinstance(limit, int) and limit > 0:
        result = result[:limit]
    return result


__all__ = ["listCandidates", "listSessionsImpl", "parseSessionInfoFromLite"]
